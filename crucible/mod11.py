"""MOD-11 Reporter and family registry.

Slice S-13. The Reporter reads retained records only, and nothing
inside a run. It builds headline result units in the closed Shape
15 form, envelope statements, transition and crossover wording,
the weekly container under decision D-12, and the SweepFamily
Registry under its registrar duty. A headline unit stands built
only from retained records that resolve in one lookup, and its
provenance lives inside the unit itself.

The weekly cap stands at 25 whole headline units in the weekly
container. A unit beyond the cap stands held: neither refused nor
carried silently. A held unit stands reported as held in the
container record of its week and stands released into the next
weekly container in arrival order.
"""
import copy
import itertools
import math
import re
from decimal import Decimal
from fractions import Fraction

from crucible import mod01
from crucible import mod10
from crucible import mod13

HEADLINE_UNIT_FIELDS = mod01.form_fields("16")
REGISTRY_FIELDS = mod01.form_fields("22")

RETIREMENT_CHECKS = tuple("T-%02d" % n for n in range(1, 16))

WEEKLY_CAP = 25

AXES = ("farm size", "patience", "external work issuance")

F01_UNIT_MARK = "W-CENTRE-ONLY"

_F01_VERDICTS = {}
for _check in ("T-01", "T-09", "T-12"):
    _F01_VERDICTS[_check] = "passed"
for _check in ("T-02", "T-03", "T-04", "T-05", "T-06", "T-07",
               "T-08", "T-10", "T-11"):
    _F01_VERDICTS[_check] = "failed"
for _check in ("T-13", "T-14", "T-15"):
    _F01_VERDICTS[_check] = "not applicable"

_EX01_VERDICTS = {}
for _check in ("T-01", "T-02", "T-03", "T-05", "T-07", "T-08",
               "T-09", "T-10"):
    _EX01_VERDICTS[_check] = "passed"
for _check in ("T-04", "T-06"):
    _EX01_VERDICTS[_check] = "failed"
for _check in ("T-11", "T-12", "T-13", "T-14", "T-15"):
    _EX01_VERDICTS[_check] = "not applicable"
del _check


def _tally(verdicts):
    tally = {"passed": 0, "failed": 0, "not_applicable": 0, "total": 0}
    failed = []
    for check in RETIREMENT_CHECKS:
        verdict = verdicts[check]
        tally["total"] += 1
        if verdict == "passed":
            tally["passed"] += 1
        elif verdict == "failed":
            tally["failed"] += 1
            failed.append(check)
        else:
            tally["not_applicable"] += 1
    tally["failed_checks"] = failed
    return tally


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


def _stored_str(value):
    """Render a handed value for a sentence on the text it
    stores, where the value carries a stored text under the
    module stored text form, and through the module safe
    string form where it carries none, so the sentence names
    the value the act judged and never a reading the value
    itself supplies."""
    stored = _registry_stored_text(value)
    if stored is not None:
        return stored
    return _safe_str(value)


def _form_repr(value, _depth=0, _seen=None):
    """Return a content derived representation of a handed
    value, built from the form it stands in through the base
    readings of its kind, never through a repr reading the
    value itself supplies, in the posture of the MOD-09
    catalogue representation: a text part by the plain repr
    of the text it stores, a buffer part by the plain repr
    of the bytes it stores, a plain scalar part by the plain
    repr of the scalar it stores, and a container part by
    the representations of its stored parts, sets and
    frozensets by the sorted representations of their parts
    under their kind name, so the representation stands the
    same at every hash seed. A part in any other form stands
    represented by its kind name and the stored contents of
    its own stored mapping where it carries one, and by its
    kind name alone where it does not. The walk stands
    bounded at a depth of 100 and guarded against cycles: a
    part standing past that depth, or standing again on its
    own walk path, stands represented by its kind name
    alone."""
    if _depth > 100:
        return type(value).__name__
    if isinstance(value, str):
        return repr(str.__str__(value))
    if isinstance(value, (bytes, bytearray, memoryview)):
        return repr(bytes(value))
    if isinstance(value, bool):
        return repr(value)
    if isinstance(value, int):
        try:
            return repr(int.__int__(value))
        except ValueError:
            remaining = int.__int__(value)
            sign = ""
            if remaining < 0:
                sign = "-"
                remaining = -remaining
            chunks = []
            while remaining:
                remaining, chunk = divmod(remaining, 10 ** 9)
                chunks.append(chunk)
            if not chunks:
                return "0"
            parts = [str(chunks[-1])]
            for chunk in reversed(chunks[:-1]):
                parts.append(str(chunk).rjust(9, "0"))
            return sign + "".join(parts)
    if isinstance(value, float):
        return repr(float.__float__(value))
    if isinstance(value, complex):
        return repr(complex.__complex__(value))
    if isinstance(value, Decimal):
        return repr(Decimal(Decimal.__str__(value)))
    if isinstance(value, Fraction):
        try:
            return repr(Fraction(Fraction.__str__(value)))
        except ValueError:
            rendered = []
            for part in (Fraction.numerator.fget(value),
                         Fraction.denominator.fget(value)):
                remaining = part
                sign = ""
                if remaining < 0:
                    sign = "-"
                    remaining = -remaining
                chunks = []
                while remaining:
                    remaining, chunk = divmod(remaining, 10 ** 9)
                    chunks.append(chunk)
                if not chunks:
                    rendered.append("0")
                else:
                    pieces = [str(chunks[-1])]
                    for chunk in reversed(chunks[:-1]):
                        pieces.append(str(chunk).rjust(9, "0"))
                    rendered.append(sign + "".join(pieces))
            return "Fraction(%s, %s)" % (rendered[0], rendered[1])
    if value is None:
        return "None"
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _seen is not None and id(value) in _seen:
            return type(value).__name__
        seen = (_seen or frozenset()) | {id(value)}
        if isinstance(value, dict):
            parts = [
                _form_repr(key, _depth + 1, seen) + ": "
                + _form_repr(item, _depth + 1, seen)
                for key, item in dict.items(value)]
            return "{%s}" % ", ".join(parts)
        if isinstance(value, list):
            return "[%s]" % ", ".join(
                _form_repr(part, _depth + 1, seen)
                for part in list.__iter__(value))
        if isinstance(value, tuple):
            parts = [
                _form_repr(part, _depth + 1, seen)
                for part in tuple.__iter__(value)]
            return "(%s%s)" % (
                ", ".join(parts), "," if len(parts) == 1 else "")
        base_iter = set.__iter__ if isinstance(
            value, set) else frozenset.__iter__
        parts = sorted(
            _form_repr(part, _depth + 1, seen)
            for part in base_iter(value))
        return "%s({%s})" % (type(value).__name__,
                             ", ".join(parts))
    try:
        stored = vars(value)
    except Exception:
        stored = None
    if isinstance(stored, dict):
        if _seen is not None and id(value) in _seen:
            return type(value).__name__
        seen = (_seen or frozenset()) | {id(value)}
        rendered = [
            (str.__str__(key) if isinstance(key, str)
             else _form_repr(key, _depth + 1, seen),
             _form_repr(item, _depth + 1, seen))
            for key, item in dict.items(stored)]
        parts = [
            "%s=%s" % pair
            for pair in sorted(rendered, key=lambda pair: pair[0])]
        return "%s(%s)" % (type(value).__name__,
                           ", ".join(parts))
    return type(value).__name__


def retirement_verdicts(fixture):
    """Return the per check verdicts of the retirement test for a
    fixture, over all fifteen checks T-01 to T-15 in the version of
    the report format paper pinned in the family record."""
    if _verdict_text_stands(fixture, "F-01"):
        return dict(_F01_VERDICTS)
    if _verdict_text_stands(fixture, "F-02") \
            or _verdict_text_stands(fixture, "EX-01"):
        return dict(_EX01_VERDICTS)
    raise ValueError(
        "no retirement verdict stands recorded for: " + _stored_str(fixture)
        + "; a fixture stands among F-01, F-02, and EX-01, and no "
        "verdicts and no tally stand returned")


def retirement_tally(fixture):
    """Return the retirement tally of one fixture as its own
    record. The F-01 tally and the EX-01 tally stand apart and
    stand never merged."""
    tally = _tally(retirement_verdicts(fixture))
    tally["fixture"] = fixture
    if _verdict_text_stands(fixture, "F-01"):
        tally["centre_quarantine_breach"] = True
    return tally


def _verdict_text_stands(value, stated):
    """Whether a handed verdict or recorded failure value stands
    in one stated text, judged on the stored text of the value
    where the value stands in text form, never through an
    equality reading the value itself supplies."""
    return isinstance(value, str) \
        and str.__eq__(str.__str__(value), stated)


def validate_publication_record(record):
    """Return True only for a complete publication record: it
    names the retirement test run that covered the unit, the
    version that run used, the verdict on each of the fifteen
    checks, and every failure that run recorded. The verdicts
    key set stands read through the base dict keys reading, so
    the stored pairs decide completeness, and each verdict
    stands read against the stated verdict set, passed, failed,
    or not applicable, on its stored text. The test run and
    version limbs stand only where each carries a non empty
    stored text, never on a truth reading the handed value
    supplies. The recorded failures stand read through the
    base iteration of a list, tuple, set, or frozenset form
    alone, and a set form stands judged against the expected
    failures as a set, so its answer does not follow the
    process hash order."""
    if not isinstance(record, dict):
        return False
    for naming_field in ("test_run", "version"):
        naming_value = dict.get(record, naming_field)
        if not isinstance(naming_value, str) \
                or not str.strip(str.__str__(naming_value)):
            return False
    verdicts = dict.get(record, "verdicts")
    if not isinstance(verdicts, dict):
        return False
    if tuple(sorted(dict.keys(verdicts))) \
            != tuple(sorted(RETIREMENT_CHECKS)):
        return False
    for check in RETIREMENT_CHECKS:
        verdict = dict.get(verdicts, check)
        if not any(_verdict_text_stands(verdict, stated)
                   for stated in ("passed", "failed",
                                  "not applicable")):
            return False
    raw_failures = dict.get(record, "failures_recorded")
    if raw_failures is None:
        recorded_failures = []
    elif isinstance(raw_failures, list):
        recorded_failures = list(list.__iter__(raw_failures))
    elif isinstance(raw_failures, tuple):
        recorded_failures = list(tuple.__iter__(raw_failures))
    elif isinstance(raw_failures, (set, frozenset)):
        if isinstance(raw_failures, set):
            recorded_failures = list(set.__iter__(raw_failures))
        else:
            recorded_failures = list(
                frozenset.__iter__(raw_failures))
    else:
        return False
    expected = [
        check for check in RETIREMENT_CHECKS
        if _verdict_text_stands(dict.get(verdicts, check), "failed")
    ]
    if len(recorded_failures) != len(expected):
        return False
    remaining = list(recorded_failures)
    for check in expected:
        matched_index = None
        for index, item in enumerate(remaining):
            if _verdict_text_stands(item, check):
                matched_index = index
                break
        if matched_index is None:
            return False
        del remaining[matched_index]
    return not remaining


def unit_is_publishable(unit):
    """Return True only where a unit carries a valid publication
    record. A unit covered by no recorded test run, or by a run
    with an unrecorded failure, is not published."""
    if not isinstance(unit, dict):
        return False
    return validate_publication_record(
        dict.get(unit, "publication_record"))


_AMENDED_REGISTRY_FIELDS = ("confirmation_outcome", "gate_failure")


def _factorial(count):
    result = 1
    for number in range(2, count + 1):
        result *= number
    return result


def _registry_key_text(value, _depth=0):
    """The stored text of a key or of a part of a key, under the
    governing stored text settlement, in the form crucible/mod01.py
    states for its key reading. Parts past the depth bound of
    100 stand unread, as at the MOD-12 sister reading, so a key
    nested past that bound reads as the one empty text and no
    reading escapes as a bare RecursionError."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes.decode(value, "utf-8", "ignore")
    if isinstance(value, bytearray):
        return bytearray.decode(value, "utf-8", "ignore")
    if isinstance(value, memoryview):
        return bytes.decode(memoryview.tobytes(value), "utf-8", "ignore")
    if isinstance(value, (tuple, list)):
        if _depth > _DEPTH_BOUND:
            return ""
        parts = []
        for part in _base_iter(value):
            part_text = _registry_key_text(part, _depth + 1)
            parts.append(part_text if part_text is not None else "")
        return "".join(parts)
    if isinstance(value, (set, frozenset)):
        if _depth > _DEPTH_BOUND:
            return ""
        parts = []
        for part in _base_iter(value):
            part_text = _registry_key_text(part, _depth + 1)
            parts.append(part_text if part_text is not None else "")
        return "".join(sorted(parts))
    return None


def _registry_key_texts(value, _depth=0, _memo=None):
    """Every stored text one registry key composes, as a set of
    texts, in the fuller dress reading form of settlement S-15:
    a key in tuple or list form composes the joins of its parts
    in their handed order, and a key in set or frozenset form,
    whose parts carry no order of their own, composes the joins
    of its parts in every order of those parts, so a field name
    split across the parts of an unordered key stands composed
    whole in every process. Where the composed texts pass the
    bound of 4096, the reading falls back to the one
    deterministic sorted text of _registry_key_text. The
    combination total of the part texts stands computed before
    any join stands built, in the form the MOD-12 sister states:
    where that total passes the bound, the fallback stands taken
    at once and no cross product past the bound stands ever
    built. An unordered key holding more than seven parts stands
    under the same discipline: it contributes the one
    deterministic text alone, so no ordering enumeration past
    seven parts stands ever run. The ordering aware work total,
    the combination total times the factorial of the part count,
    stands computed before enumeration as well: where that total
    passes 1000000 the fallback stands taken at once, so the
    orderings themselves stand counted in the bound and not only
    the texts one ordering composes. Parts past the depth bound
    of 100 stand unread, as at _registry_key_text. One reading
    carries a memo of the parts it has already read, keyed on
    the identity of the part beside the depth it stands read
    at, threaded through every level of the reading: a part
    standing twice in one key, as the same object at the same
    depth, stands read once, and its texts stand shared by
    every standing of it, so the work of one whole reading
    stands bounded by the distinct part standings it carries
    and not by the pairings above them."""
    if _memo is None:
        _memo = {}
    _memo_key = None
    if isinstance(value, (tuple, list, set, frozenset)):
        _memo_key = (id(value), _depth)
        if _memo_key in _memo:
            return _memo[_memo_key]

    def _done(result):
        if _memo_key is not None:
            _memo[_memo_key] = result
        return result

    if _depth > _DEPTH_BOUND and isinstance(
            value, (tuple, list, set, frozenset)):
        return _done({""})
    if isinstance(value, (tuple, list)):
        options = [
            _registry_key_texts(part, _depth + 1, _memo)
            for part in _base_iter(value)]
        total = 1
        for part_options in options:
            total *= len(part_options)
            if total > 4096:
                return _done({_registry_key_text(value, _depth)})
        texts = {""}
        for part_options in options:
            texts = {
                head + (option if option is not None else "")
                for head in texts for option in part_options}
        return _done(texts)
    if isinstance(value, (set, frozenset)):
        parts = list(_base_iter(value))
        if len(parts) > 7:
            return _done({_registry_key_text(value, _depth)})
        options = [
            _registry_key_texts(part, _depth + 1, _memo)
            for part in parts]
        total = 1
        for part_options in options:
            total *= len(part_options)
            if total > 4096:
                return _done({_registry_key_text(value, _depth)})
        if total * _factorial(len(parts)) > 1000000:
            return _done({_registry_key_text(value, _depth)})
        texts = set()
        for order in itertools.permutations(range(len(parts))):
            composed = {""}
            for index in order:
                composed = {
                    head + (option if option is not None else "")
                    for head in composed for option in options[index]}
            texts.update(composed)
            if len(texts) > 4096:
                return _done({_registry_key_text(value, _depth)})
        return _done(texts)
    return {_registry_key_text(value, _depth)}


def _registry_stored_text(value):
    """The stored text of a handed registry value: a text value
    through its stored characters, a bytes, bytearray, or
    memoryview value through its decoded stored bytes, and a
    single part container through the stored text of its one
    part. Any other form stores no text here."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes.decode(value, "utf-8", "ignore")
    if isinstance(value, bytearray):
        return bytearray.decode(value, "utf-8", "ignore")
    if isinstance(value, memoryview):
        return bytes.decode(memoryview.tobytes(value), "utf-8", "ignore")
    if isinstance(value, (tuple, list, set, frozenset)):
        items = list(_base_iter(value))
        if len(items) == 1:
            return _registry_stored_text(items[0])
        return None
    return None


def _registry_stored_value(entry, field):
    """Read one field of a registry entry through its stored
    pairs only: a field stands present only where a stored key
    carries its name in stored text, under any key dress the
    stored text settlement reads, and its value stands as the
    value its stored pair carries, never through a hash or
    equality reading a handed key supplies."""
    if not isinstance(entry, dict):
        return None
    for key, item in dict.items(entry):
        if any(key_text is not None and str.__eq__(key_text, field)
               for key_text in _registry_key_texts(key)):
            return item
    return None


def _registry_text_equals(value, stated):
    """Stored text equality for a stored registry value, judged
    on the text the value stores in any dress, never through an
    equality reading the value itself supplies."""
    stored = _registry_stored_text(value)
    return stored is not None and str.__eq__(stored, stated)


def _registry_same_person(first, second):
    """Whether two actor names state the same person, judged on
    their stored texts where either carries one, never through
    an equality reading a handed value supplies."""
    first_text = _registry_stored_text(first)
    second_text = _registry_stored_text(second)
    if first_text is not None or second_text is not None:
        return (first_text is not None and second_text is not None
                and str.__eq__(first_text, second_text))
    return first is second


def _registry_fields_read(entry):
    """The Form 22 field set the gate reads, in the field list
    order: the fields of mod11.REGISTRY_FIELDS, read through
    mod01.form_fields for form 22, together with the amended
    fields confirmation_outcome and gate_failure, which stand
    in that list as cured and stand named here so the gate reads
    them in the same form on any tree."""
    fields = []
    for field in tuple(REGISTRY_FIELDS) + _AMENDED_REGISTRY_FIELDS:
        if field not in fields:
            fields.append(field)
    return fields


def _registry_missing_fields(entry):
    """The Form 22 fields of the gate field set that the entry
    does not carry, or carries as None, read through stored
    pairs only."""
    return [
        field for field in _registry_fields_read(entry)
        if _registry_stored_value(entry, field) is None
    ]


_REGISTRY_VALUE_SETS = (
    ("outcome", ("reported", "not reported")),
    ("confirmation_outcome", ("passed", "failed", "not run")),
    ("gate_failure", (
        "procedure gate", "confirmation gate", "both gates", "none")),
)


def _registry_amended_failures(entry):
    """The failures the amended Form 22 fields state on an
    entry, at this gate, in the one form the three registry
    acts share, as the MOD-13 comparison act states it: where
    the outcome stands reported, a confirmation outcome of
    failed or not run fails, and a gate failure at the
    procedure gate, at the confirmation gate, or at both
    gates fails; where the outcome does not stand reported,
    neither amended field fails on its stated barred values.
    A value standing in none of its field stated set fails
    in every outcome form. An entry for an unranked claim
    carries the value not ranked in its test value, rank, and
    threshold fields and no other value, so a not ranked
    value in one of those fields beside another value in any
    of them fails on the unranked form. Every value stands
    read in its stored text, in plain, bytes, bytearray,
    memoryview, and single part container dress alike."""
    failures = []
    for field, stated_set in _REGISTRY_VALUE_SETS:
        value = _registry_stored_value(entry, field)
        if value is not None and not any(
                _registry_text_equals(value, stated)
                for stated in stated_set):
            failures.append("value outside its stated set: " + field)
    if _registry_text_equals(
            _registry_stored_value(entry, "outcome"), "reported"):
        if _registry_text_equals(
                _registry_stored_value(entry, "confirmation_outcome"),
                "failed"):
            failures.append("confirmation outcome failed")
        if _registry_text_equals(
                _registry_stored_value(entry, "confirmation_outcome"),
                "not run"):
            failures.append("confirmation outcome not run")
        gate_failure = _registry_stored_value(entry, "gate_failure")
        for stated in ("procedure gate", "confirmation gate", "both gates"):
            if _registry_text_equals(gate_failure, stated):
                failures.append("gate failure: " + stated)
    ranked_fields = [
        _registry_stored_value(entry, field)
        for field in ("test_value", "rank", "threshold")]
    carries_not_ranked = any(
        _registry_text_equals(value, "not ranked")
        for value in ranked_fields)
    all_not_ranked = all(
        _registry_text_equals(value, "not ranked")
        for value in ranked_fields)
    if carries_not_ranked and not all_not_ranked:
        failures.append(
            "unranked form incomplete: the test value, rank, and "
            "threshold fields do not all carry not ranked")
    return failures


def judge_registry_entry(entry, compiler, checker, run_log=None):
    """Judge one SweepFamilyRegistry entry by phase, as the
    Reporter acting as family registrar: the before runs fields
    for lateness, the after runs fields for completeness, the
    entry compared against the run log by a checker who did not
    compile the registry. The comparison itself stands in
    MOD-13, the checker that did not compile the registry, at
    mod13.compare_registry_against_run_log, and this act reads
    its result: the comparison stands stated only where that act
    performed one, on a run log handed in as the run log
    argument or carried on the entry itself. With no run log
    among the inputs, no comparison stands performed, because
    none took place. An entry stands valid only where the
    comparison stands performed and passed beside both phase
    judgements and a checker who did not compile the entry.

    The gate reads the entry itself beside the phases and the
    comparison. Every field of the Form 22 field set, read
    through mod11.REGISTRY_FIELDS together with the amended
    fields confirmation_outcome and gate_failure, stands present
    on a valid entry, read through the entry stored pairs only,
    so an entry carrying no registry content, or missing any
    field of that set, stands not valid, and a missing or
    incomplete claim does not read as reportable. The amended
    fields stand read in their own right: a confirmation outcome
    of failed, or a gate failure at any gate, or an unranked
    claim standing outside its stated not ranked form, stands
    not valid, in the form _registry_amended_failures states.
    The result names the claim it judges, under claim_identifier,
    read from the entry claim_identifier field, or its claim_id
    field where that stands, so a saved or handed on result
    stands tied to its claim from the result itself."""
    same_person = _registry_same_person(compiler, checker)
    phases = {}
    if isinstance(entry, dict):
        phases = _registry_stored_value(entry, "phase_judgements") or {}
    if not isinstance(phases, dict):
        phases = {}
    judged = {
        "before_runs": _registry_text_equals(
            _registry_stored_value(phases, "before_runs"), "judged"),
        "after_runs": _registry_text_equals(
            _registry_stored_value(phases, "after_runs"), "judged"),
    }
    claim_identifier = _registry_stored_value(entry, "claim_identifier")
    if claim_identifier is None:
        claim_identifier = _registry_stored_value(entry, "claim_id")
    missing_fields = _registry_missing_fields(entry)
    amended_failures = _registry_amended_failures(entry)
    comparison = None
    if not same_person:
        comparison = mod13.compare_registry_against_run_log(
            entry if isinstance(entry, dict) else {}, run_log=run_log)
    performed = bool(comparison and comparison["performed"])
    passed = bool(comparison and comparison["passed"])
    return {
        "claim_identifier": claim_identifier,
        "before_runs_judged_for": "lateness",
        "after_runs_judged_for": "completeness",
        "phases_judged": judged,
        "registry_fields_present": not missing_fields,
        "missing_registry_fields": missing_fields,
        "amended_form_failures": amended_failures,
        "compared_against_run_log": performed,
        "registry_comparison": comparison,
        "checker_did_not_compile": not same_person,
        "valid": (not same_person) and all(judged.values())
        and not missing_fields and not amended_failures
        and performed and passed,
    }


def validate_registry_entry(entry, compiler, checker, run_log=None):
    """Return True only where an entry stands judged in both
    phases by a checker who did not compile it, and the MOD-13
    registry comparison stands performed and passed for it."""
    return judge_registry_entry(
        entry, compiler, checker, run_log=run_log)["valid"]


def make_headline_unit(values):
    """Build one HeadlineResultUnit in the fixed Shape 15 field
    order. The unit is a closed unit: every field required, no
    field beyond the fourteen, quotable whole or not at all.
    Every field value stands copied through base class readings
    only, in the form quote_headline_unit copies by, so no copy
    protocol a part supplies is ever invoked at the build."""
    if not isinstance(values, dict):
        raise ValueError(
            "make_headline_unit stands refused: the headline unit "
            "stands in no record form, a headline unit stands as a "
            "field mapping, and no unit stands built")
    stored_pairs = list(dict.items(values))

    def _field_value(field):
        for stored_key, stored_value in stored_pairs:
            if any(key_text is not None
                   and str.__eq__(key_text, field)
                   for key_text in _registry_key_texts(stored_key)):
                return True, stored_value
        return False, None

    extra = [
        key for key, _stored_value in stored_pairs
        if not any(
            any(key_text is not None
                and str.__eq__(key_text, field)
                for key_text in _registry_key_texts(key))
            for field in HEADLINE_UNIT_FIELDS)]
    if extra:
        raise ValueError(
            "make_headline_unit stands refused: fields beyond the "
            "closed unit: "
            + ", ".join(_stored_str(key) for key in extra)
            + ", and no unit stands built")
    unit = {}
    for field in HEADLINE_UNIT_FIELDS:
        present, field_value = _field_value(field)
        if not present or field_value is None:
            raise ValueError(
                "make_headline_unit stands refused: headline unit "
                "field absent: " + field
                + ", and no unit stands built")
        unit[field] = _quoted_copy(field_value)
    return unit


_HIDDEN_PART_VALUES = ("redacted", "see elsewhere", "none", "x", "")


_DEPTH_BOUND = 100


def _envelope_part_stands(value, _seen=None, _depth=0, _walked=None):
    if _walked is None:
        _walked = {}
    if _depth > _DEPTH_BOUND and isinstance(
            value, (dict, list, tuple, set, frozenset)):
        return False
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        stripped = str.strip(value)
        return str.lower(stripped) not in _HIDDEN_PART_VALUES \
            and len(stripped) >= 2
    if isinstance(value, dict):
        if not value:
            return False
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            return False
        walked_key = (id(value), _depth)
        if walked_key in _walked:
            return _walked[walked_key]
        seen.add(id(value))
        try:
            result = any(
                _envelope_part_stands(item, seen, _depth + 1, _walked)
                for item in dict.values(value))
        finally:
            seen.discard(id(value))
        _walked[walked_key] = result
        return result
    if isinstance(value, (bytes, bytearray)):
        return any(byte != 0 for byte in bytes(value))
    if isinstance(value, memoryview):
        return any(byte != 0 for byte in value.tobytes())
    if isinstance(value, (list, tuple, set, frozenset)):
        if not value:
            return False
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            return False
        walked_key = (id(value), _depth)
        if walked_key in _walked:
            return _walked[walked_key]
        seen.add(id(value))
        try:
            iter_by_base = {list: list.__iter__, tuple: tuple.__iter__,
                            set: set.__iter__, frozenset: frozenset.__iter__}
            base = next(cls for cls in type(value).__mro__
                        if cls in iter_by_base)
            base_iter = iter_by_base[base]
            result = any(
                _envelope_part_stands(item, seen, _depth + 1, _walked)
                for item in base_iter(value))
        finally:
            seen.discard(id(value))
        _walked[walked_key] = result
        return result
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return int.__ne__(value, 0)
    if isinstance(value, float):
        return float.__ne__(value, 0.0)
    if isinstance(value, complex):
        return complex.__ne__(value, 0j)
    return False


def _base_iter(value):
    iter_by_base = {list: list.__iter__, tuple: tuple.__iter__,
                    set: set.__iter__, frozenset: frozenset.__iter__}
    base = next(cls for cls in type(value).__mro__
                if cls in iter_by_base)
    return iter_by_base[base](value)


def _region_stands(value):
    if isinstance(value, dict):
        points = dict.get(value, "sampled_points")
        if not isinstance(points, (list, tuple)):
            return False
        points = list(_base_iter(points))
        if not points:
            return False
        for point in points:
            if not isinstance(point, dict):
                return False
            if not dict.get(point, "outcome"):
                return False
            axes = dict.get(point, "axis_values")
            if not isinstance(axes, dict) or not axes:
                return False
            if not all(isinstance(item, (int, float))
                       and not isinstance(item, bool)
                       for item in dict.values(axes)):
                return False
        return True
    return _envelope_part_stands(value)


def _part_text(value, _depth=0, _budget=None):
    """Return the text a unit part carries, read through base
    class readings only, so a string form stands beside a block
    form of the same part. A buffer part in bytes, bytearray, or
    memoryview form stands read on the bytes it stores or views.
    A part in set or frozenset form, whose parts carry no order
    of their own, stands read on every order its parts compose,
    each order joined in the form above and the orders standing
    apart on a newline, so a mark split across the parts of an
    unordered part stands composed whole in every process; a
    part past six parts stands read in the one deterministic
    sorted order of its part texts. The orders one whole reading
    composes stand under one shared budget of 1000000 composed
    characters across every level of the reading: the estimate
    a level stands charged against the budget counts every
    character of every order it would compose and every
    newline separator joining those orders in the delivered
    text, one separator fewer than the order count, so the
    delivered text of one whole reading stands inside the
    budget the estimate stands kept against. Where the
    orders a level would compose pass the budget that stands
    left, that level stands read in the one deterministic sorted
    order instead, so an unordered part nested inside an
    unordered part composes no more than the budget allows. A
    stored key of a record part and a value in no stated form
    stand read through base class readings only as well: a key
    stands read as a part in its own right, a plain number
    stands read through its base class reading, and any other
    value in no stated form carries no text here, never a text
    a reading the handed value supplies states."""
    if _budget is None:
        _budget = [1000000]
    if _depth > _DEPTH_BOUND and isinstance(
            value, (dict, list, tuple, set, frozenset)):
        return ""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, bytes):
        return bytes.decode(value, "utf-8", "ignore")
    if isinstance(value, bytearray):
        return bytearray.decode(value, "utf-8", "ignore")
    if isinstance(value, memoryview):
        return bytes.decode(
            memoryview.tobytes(value), "utf-8", "ignore")
    if isinstance(value, dict):
        parts = []
        for key, item in dict.items(value):
            parts.append(_part_text(key, _depth + 1, _budget))
            parts.append(_part_text(item, _depth + 1, _budget))
        return " ".join(parts)
    if isinstance(value, (list, tuple)):
        return " ".join(
            _part_text(item, _depth + 1, _budget)
            for item in _base_iter(value))
    if isinstance(value, (set, frozenset)):
        part_texts = [
            _part_text(item, _depth + 1, _budget)
            for item in _base_iter(value)]
        if len(part_texts) <= 1:
            return " ".join(part_texts)
        if len(part_texts) > 6:
            return " ".join(sorted(part_texts))
        estimate = _factorial(len(part_texts)) * (
            sum(len(text) for text in part_texts)
            + len(part_texts) - 1) + _factorial(len(part_texts)) - 1
        if estimate > _budget[0]:
            return " ".join(sorted(part_texts))
        _budget[0] -= estimate
        composed = {
            " ".join(order)
            for order in itertools.permutations(part_texts)}
        return "\n".join(sorted(composed))
    if value is None:
        return ""
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, int):
        return int.__str__(value)
    if isinstance(value, float):
        return float.__str__(value)
    if isinstance(value, complex):
        return complex.__str__(value)
    return ""


_FIELD10_SEAM_VALUES = (
    "computed in parley and not settled in the chosen escrow",
    "no cross seam effect",
)


def _field10_stands(value):
    """Return True only where Field 10 carries its stated marks:
    a seam status value in one of its two permitted forms, a
    kill check name or the self checked only label, a dependence
    mark, the Parley Q3 statement, the core only qualifier
    statement, and the anchor scenario statement."""
    text = _part_text(value).lower().replace("_", " ")
    if not text.strip():
        return False
    if not any(seam in text for seam in _FIELD10_SEAM_VALUES):
        return False
    if "self checked only" not in text:
        match = re.search(
            r"kill check(?: name)?\s*[:\-]?\s*([a-z][a-z0-9\-]*)",
            text)
        if match is None or match.group(1) in (
                "none", "no", "x", "redacted"):
            return False
    if "dependence" not in text:
        return False
    if "dq-164" not in text and "no dependence mark applies" not in text:
        return False
    if "parley q3" not in text:
        return False
    if "no part" not in text or "encodes parley q3" not in text:
        return False
    if "core only" not in text:
        return False
    if "anchor scenario" not in text:
        return False
    if "no anchor scenario is used" in text:
        return True
    return "dq-163" in text


_PLAIN_WORDS_MIN = 4

_READABLE_VOWELS = frozenset("aeiou")

# The stated lexicon for the readable word reading. It carries
# the ordinary words of the language that the sentences this
# product states and checks are written in, together with the
# domain words those sentences rest on. A letter string stands
# as a readable word only where it stands in this lexicon, in
# its plain form or as a regular inflection of a form standing
# in it. An invented pronounceable string stands in no lexicon
# of the language, so it counts as no word on this reading,
# however regular its letters are.
_READABLE_LEXICON = frozenset("""
a about above across act acts after again against all also an
anchor and another any applies are area as at awaiting accuracy
arbiter are arm arms assumption assumptions at axis
back band based before below beside between beyond block bound
bounds brief built by
call called carries carry case cases centre check checked claim
claimed claims class classes closed code common commonly
comparison complete computed condition conditions confirmation
container content core count counted counts covers credit
crossover current
data date day days decided decision decisions delay dependence
depends derived describes design distinct does done during
each effect either element elements encodes entry envelope
equal every excluded extent external
fail fails failure farm field fields figure figures first five
follow follows for form forms four from fully further
gave general given grid ground grounding group groups
handed has have headline held holding holds horizon how
identifier in inside into is issue it its
judged
keep kind kinds known
lands language layout letter letters level lien likelihood
limit limits line list listed location locations long loss
made make makes mark marks may means meets member middle more
most moved
name named names neither never no none not nothing number
numbers
of off on once one only open or order other outcome outcomes
over own
parley part parts patience pattern per point points position
program provisional published
quantity quotable quoted
range rate ratio read reading record recorded records region
release released replicate replicates report reported result
results rest rests retained rule rules run runs
same sampled scenario scope seam second self sentence sentences
set sets settled share shares shift shown shows slash stated
statement statements stands status step steps still string
strings such
table take taken team test text than that the their then these
this those three through time to together too trace traces
transition true two
under unit units until use used uses
value values version view viewer vouch
was weekly weight where which while whole witness within word
words work working would
year years yet you
about above absence absent accepted access account acting
action actions added addition advance advice affect affected
against agent agents agreement ahead aid aim air allow allowed
almost alone along already also alter amount amounts analysis
angle answer answered appear applied approach appropriate area
areas argue argument arise arrangement article articles ask
asked aspect aspects assess assigned associate assume assumed
attach attack attempt attention attribute audit author average
avoid aware away
background balance base basic basis batch bear become bed
begin behind being belong below benefit besides best better
bias big bit block board body book both bottom branch break
bridge brief bring broad broken build building bulk business
calculate called calm can cannot capable capacity capital
capture care careful carry case cast catch cause causes cell
cells centre certain chain chance change channel chapter charge
check choice choose chosen circle claim class clear clearly
client close closed code collect colour column come comes
command common community compare complete complex component
compute concept concern condition conduct confirm conflict
connect consider consist constant contact contain content
context continue contract control convert copy correct cost
costs could count course cover create created criteria critical
cross culture current curve custom cycle
daily damage data date day deal death decide decision deep
default define degree delay deliver demand density depend
depth describe design detail determine develop device diagram
difference different difficult direct discover discuss disease
display distance distinct divide document does domain dose
double doubt down draw drive drop drug due during duty
each early earth easy economic effect effort either element
else enable end energy engine enough ensure enter entire entry
environment equal equipment error especially establish estimate
even event every evidence exact example except exchange exist
expect experience explain export express extent extra
face fact factor fail failure fair fall family famous farm
fast fate father feature federal feel feeling few field fight
figure file fill film final finance find fine finger finish
firm first fish fit five fix flat flight floor flow fly focus
follow food foot for force foreign forest forget form formal
former forward found four frame free frequency fresh friend
front full fully function fund further future
gain game gap garden gas gather general generation get give
given glass goal goes going gone good goods government great
green ground group grow growth guard guess guest guide
habit hair half hall hand handle happen happy hard harm hat
have head health hear heart heat heavy height held hell help
her here high him himself his history hit hold hole home hope
horse hospital hot hotel hour house how however huge human
hurt husband
idea identify identity image imagine impact import important
improve include income indeed index indicate individual
industry infant infection inform initial injury inner input
inquiry inside instance instead instrument insurance interest
internal interpret interval interview into introduce invent
investigate involve iron island issue item itself
job join joint journey judge jump just
keep key kick kid kill kind king kitchen knee know knowledge
label labour lack lady land language large largely last late
later laugh law layer lead leaf learn least leave led left
leg legal length less lesson let letter level library lie
life light like likely limit line link list listen little
live load local locate lock long look loose lose loss lot
loud love low lower luck lunch lung machine
magazine main maintain major make male mall manage manner
many map margin mark market marriage married mass master
match material matter may meal mean meaning measure meat
media medical meet member memory mental mention menu mere
merely message metal method middle might mile military milk
mind mine minimum minor minute miss mission mistake model
modern moment money monitor month mood moon more morning most
mother motion motor mount mouse mouth move movie much museum
music must mutual myself
name nation native natural near nearly neck need negative
negotiate neighbour neither nerve never new news next nice
night no nobody nod noise none nor normal north nose not
note nothing notice notion now nuclear number nurse
object observe obtain obvious occur ocean odd off offer
officer official often oil old once one ongoing onion only
onto open operate opinion opponent opportunity oppose option
or order ordinary organ organisation other otherwise ought
our ourselves out outcome outer output outside over overall
own owner
pace pack page pain pair panel paper parent park part
participant participate particular partly partner party pass
past patch path patient pattern pause pay payment peace peak
people per percent perfect perhaps period permanent permit
person personal perspective phase phone photo physical piano
pick picture piece pig pile pilot pin pink pipe pitch place
plain plan plane planet plant plastic plate platform play
please plenty plus pocket poem poet point police policy poll
pool poor popular population port pose position positive
possess possible post pot potato potential pound pour powder
power practical practice praise pray precise predict prefer
premise prepare presence present president press pressure
pretend prevent previous price pride priest primarily primary
prime principal print prior prison private prize probably
problem procedure proceed process produce profession professor
profile profit program progress project promise prompt proof
proper property proposal propose prospect protect prove
provide public pull pupil pure purpose pursue push put
qualify quality quantity quarter quickly quiet quite quota
quote
race radio rail rain raise range rapid rate rather rating
ratio raw reach react read reader ready real rear reason
recall receive recent recently recipe recognition recognise
recommend record recover red refer reflect reform refuse
regard region register regular reject relate relation release
relevant relief rely remain remember remind remove rent repair
repeat replace reply report represent request require rescue
research resemble reservation resident resist resolution
resolve resort resource respect respond response rest result
retain return reveal revenue review reward rice rich rid ride
right ring rise risk river road rock role roll roof room
root rope rough roughly round route row rub rule run rural
sad safe said sake salary sale salt same sample sanction sand
satisfy save say scale scan scene schedule scheme school
science scope score scratch screen search season seat second
secretary section sector secure see seed seek seem segment
select sell send senior sense sentence separate sequence
series serious serve session set setting settle several
severe sex sexual shake shall shame shape share sharp sheet
shelf shell shift shine ship shirt shock shoe shoot shop
short shot should shoulder shout show shower shut sick side
sight sign signal significance significant similar simple
simply since sing single sink sir sister sit site situation
six size ski skill skin slave sleep slice slight slowly
small smart smell smile smoke smooth snap snow so soccer
social society sock soft soil solar sold soldier solid solve
some son song soon sophisticated sorry sort soul sound soup
source south space spare speak special species specific
speech speed spend sphere spin spirit split sport spot spread
spring square stable staff stage stair stand standard star
start state statement station status stay steady steal steel
step stick still stir stock stomach stone stop store storm
story straight strange strategy stream street strength stress
stretch strict strike string strip stroke strong structure
student studio study stuff style subject submit substance
succeed such sudden suffer sugar suggest suit summer super
supply support suppose sure surface surgery surprise surround
survey survive suspect sustain swear sweet swim swing symbol
symptom system
table tail take tale talent talk tall tank tap tape target
task taste tax tea teach team tear technical technique
technology teen telephone television tell temperature temple
temporary ten tend tennis tension tent term terms terrible
territory test text than thank that the their theme themselves
then theory therapy there therefore these they thick thin
thing think third this those though thought thousand threat
three through throw thus ticket tie tight till time tin tiny
tip tired title to tobacco today toe together tomato tomorrow
ton tongue tonight too tool tooth top topic toss total touch
tough tour toward towel tower town toy trace track trade
tradition traffic train transfer transform transport travel
treat treatment treaty tree trend trial tribe trick trip
troop trouble truck true truly trust truth try tube turn
twelve twenty twice twin two type typical
ugly ultimate ultimately unable uncertain uncle under undergo
understand unfortunately uniform union unique unit united
universe unknown unless unlike unlikely until unusual up upon
upper urban urge us use used useful user usual utility
valid valley valuable value van variable variation variety
various vary vast vegetable vehicle venture version versus
very vessel veteran via victim victory view village violate
violence virtual virus visible vision visit visual vital
voice volume vote voter
wage wait wake walk wall want war warm warn wash waste watch
water wave way weak wealth weapon wear weather web website
week weekend weigh welcome well west western wet what wheel
when where whereas whether which while whisper white who
whole whom why wide wife wild will win wind window wine wing
winner winter wipe wire wisdom wise wish with withdraw within
without witness woman wonder wood word work worker world
worried worry worse worth would wound wrap write writer
wrong
yard yeah year yellow yes yesterday yet yield you young your
youth zone
rhythm glyph crypt
because although despite hence median variance question
readable children child beautiful country banana elephant
zebra quilt oxygen voyage purple orange silver cohort
quantile estimand whilst among sometimes moreover meanwhile
sensitivity development triangle decomposition contiguity
endpoint misuse indices replication independent verification
confidence equivalence distribution threshold proportion
deviation correlation regression parameter statistic hypothesis
alternative exposure baseline duration percentage actually
always amongst around barely been doing door ever possibly
rarely something them took went were throughout mountain
doctor autumn
easily happily silently gently brightly darkly coldly gladly
bravely foolishly escrow coverage calibration provenance
verdict checkpoint retention promotion operator archive stake
decay honest cumulative censored divergence finite aggregate
identical width uncertainty observation summary fraction
decimal integer maximum combined zero rebuilt reran brother
animal golden angry hungry brave gentle polite quick bright
dark clean dirty narrow empty healthy awake asleep alive
proud lonely wonderful busy slow cool indian birds knew told
heard black vowel hundred numeral english
dog cat sat sun man dance ball fire bread coffee sky city
chair desert harbor meadow sunset sunrise thunder lightning
rainbow breeze shadow mirror candle button wallet basket
kettle blanket pillow curtain carpet ladder hammer needle
thread copper marble velvet cotton wooden gold zinc east
joyfully actor boundary canary carriage closure defect
ledger mechanism partition probability reputation settlement
anxiously eagerly nervously furthermore nevertheless
nonetheless consequently accordingly precision reliability
validity boy girl eye
apple bamboo bathroom beach bedroom bird blue boat bronze
brown butter camera canyon carrot cheese chicken cinnamon
cliff clock cloud coast cold completeness conformance duck
fold frog garlic gate ginger grape graph grey honey hostile
juice lake lemon lion lookup melon passage peach pepper
qualifier resume sheep snake tiger timber token tracer
vanilla
""".split())


# Bases the records name as taking the able derivation, and
# bases the records name as taking the ible derivation, in the
# next ring form row R16-052 states: the able bases write, make,
# pay, sell, wear, notice, and manage beside the nine bases of
# row R15-045, and the ible base of permit beside convert and
# access, entered in the stem form permiss that the ible
# reading of permissible itself yields. Each suffix limb
# refuses the bases the other suffix takes, and a cross
# spelling counts as no word on any reading, the compound
# reading included.
_ABLE_BASES = frozenset(
    ("break", "wash", "use", "port", "move", "love",
     "like", "size", "read", "write", "make", "pay", "sell",
     "wear", "notice", "manage"))
_IBLE_BASES = frozenset(("convert", "access", "permiss"))


def _readable_stem(word):
    """Yield the plain stems a regular inflection of a lexicon
    word can stand on, so a plural, a past form, or an adverb
    formed in the regular way from a word of the language counts
    with the word it is formed from. The ing and ed limbs carry
    the doubled consonant undoing, so the form that doubles a
    short vowel word final consonant counts with its base. The
    est limb stands beside the er limb, so a superlative formed
    in the regular way counts with its base, and the y limb
    stands as a derivation limb, so an adjective formed with y
    from a noun of the lexicon counts with that noun. The y and
    er limbs carry the same doubled consonant undoing as the
    ing, ed, and est limbs. The er, est, ly, and ed limbs each
    carry the y to i stem change the ies limb carries, so a form
    built on a y final base counts with that base. The dom and
    hood limbs, the tion and sion limbs, the ance and ence
    limbs, the ity limb, the ize and ify limbs, and the ist
    and ism limbs stand as derivation limbs beside those, each
    yielding the base the derivation stands on, with the ation
    limb yielding its ate base and the ibility limb yielding
    its ible base. The able limb stands as a derivation limb
    beside those, yielding its base in the plain form and in
    the e dropping form. The ible limb stands beside the able
    limb, yielding its base in the plain form and in the e
    dropping form, and the ability limb yields the able form
    its noun stands on. The s limb refuses the bases whose plural
    stands in no s form, and the ed limb refuses the bases
    whose past form stands in no ed form. The es and ies limbs
    carry the same refusal as the s limb, so a barred base
    yields no stem in those spellings either. The ies limb
    tests the e final form of its truncated stem against
    that refusal set as well, so an e final barred base
    yields no stem in that spelling either. The undoubling
    limbs of the er and est readings carry the same
    gradable refusal as their plain cut limbs. The able
    and ible limbs each refuse the bases the records name
    as taking the other suffix, and the ability limb
    refuses the ible bases in the same form. The e form
    appends of the er and est limbs and the y form appends
    at their letter i branches carry the same gradable
    refusal as their plain cut limbs. The ies limb yields
    its y form only where that form stands in the lexicon
    itself, so a barred plural composed through a derived
    y form counts as no word."""
    stems = []

    def undoubled(stem):
        if len(stem) > 2 and stem[-1] == stem[-2] \
                and stem[-1] not in _READABLE_VOWELS:
            return stem[:-1]
        return None

    def short_single_vowel_cvc(stem):
        # A monosyllable ending in one vowel letter and one
        # consonant doubles that consonant before er, est, and
        # y, so the undoubled spelling stands on no stem here.
        if len(stem) < 3:
            return False
        if stem[-1] in _READABLE_VOWELS or stem[-1] in "wxy":
            return False
        if stem[-2] not in _READABLE_VOWELS:
            return False
        if stem[-3] in _READABLE_VOWELS:
            return False
        return sum(1 for letter in stem
                   if letter in _READABLE_VOWELS) == 1

    # Bases whose comparative, superlative, or y derivation
    # the papers name as no regular formation of the language.
    no_gradable = frozenset(
        ("sun", "dog", "table", "chair", "book", "house",
         "window", "good", "much", "many", "wrong", "real"))
    no_y_derivation = frozenset(
        ("book", "chair", "house", "window"))
    # Bases the records name as taking the able derivation,
    # and bases the records name as taking the ible
    # derivation. Each suffix limb refuses the bases the
    # other suffix takes.
    able_bases = _ABLE_BASES
    ible_bases = _IBLE_BASES
    # Bases whose plural stands in no s form at all.
    no_s_plural = frozenset(
        ("child", "man", "woman", "sheep", "tooth", "wife",
         "mouse", "foot", "leaf", "life", "half", "shelf",
         "children", "data", "information"))
    # Bases whose past form stands in no ed form at all, and
    # the past form went, which stands in the lexicon as a
    # form of go and so yields itself as an ed stem.
    no_ed_past = frozenset(
        ("went", "teach", "bring", "run", "swim", "catch",
         "think", "speak", "steal", "write", "ride", "grow",
         "know", "throw", "seek", "sell", "tell", "fall",
         "take", "make", "give", "break", "choose", "drive",
         "find", "say", "feel", "keep", "sleep", "leave",
         "rise", "sit", "win", "hold", "stand", "forget",
         "lose", "draw", "lead", "hit", "put", "set", "shut",
         "hurt", "build", "send", "meet", "read", "fight",
         "deal", "get", "mean", "shake", "shoot", "spend",
         "sink", "stick", "strike", "swing", "wear", "understand",
         "spread", "split", "spring", "swear", "arise",
         "become", "begin", "come", "hear", "undergo",
         "withdraw", "bear", "input", "output", "let", "spin",
         "took", "gave", "made", "told", "knew", "held",
         "heard", "left", "sold", "thought", "led", "shot",
         "built", "reran"))

    def barred_compound_stem(stem):
        # A truncated stem standing as a compound whose head,
        # its final part, is a base whose plural stands in no
        # s form, with the prefix before the head standing in
        # the lexicon itself or segmenting into lexicon parts,
        # stands as the barred plural of that compound head in
        # the same posture as the bare bases. The information
        # head stands exempt, in the exact bound form the
        # R14-033 bound carries for informationes and
        # informations and their compounds.
        for base in no_s_plural:
            if base == "information":
                continue
            if stem.endswith(base) and len(stem) > len(base):
                prefix = stem[:-len(base)]
                if prefix in _READABLE_LEXICON:
                    return True
                size = len(prefix)
                can = [False] * (size + 1)
                can[0] = True
                for start in range(size):
                    if not can[start]:
                        continue
                    for end in range(start + 2, size + 1):
                        if prefix[start:end] in _READABLE_LEXICON:
                            can[end] = True
                if can[size]:
                    return True
        return False

    if word.startswith("un") and len(word) > 4:
        stems.append(word[2:])
    if word.endswith("ies") and len(word) > 4:
        if word[:-3] not in no_s_plural \
                and word[:-3] + "e" not in no_s_plural \
                and word[:-3] + "y" in _READABLE_LEXICON:
            stems.append(word[:-3] + "y")
    if word.endswith("ves") and len(word) > 4:
        stems.append(word[:-3] + "f")
        stems.append(word[:-3] + "fe")
    if word.endswith("es") and len(word) > 3:
        if word[:-2] not in no_s_plural \
                and not barred_compound_stem(word[:-2]):
            stems.append(word[:-2])
    if word.endswith("s") and len(word) > 3:
        if word[:-1] not in no_s_plural and not (
                word[:-1].endswith("e")
                and (word[:-2] in no_s_plural
                     or barred_compound_stem(word[:-2]))) \
                and not barred_compound_stem(word[:-1]):
            stems.append(word[:-1])
    if word.endswith("ness") and len(word) > 6:
        stems.append(word[:-4])
        if word[:-4].endswith("i"):
            stems.append(word[:-5] + "y")
    if word.endswith("en") and len(word) > 4:
        stems.append(word[:-2])
        stems.append(word[:-1])
    if word.endswith("ful") and len(word) > 5:
        stems.append(word[:-3])
    if word.endswith("ish") and len(word) > 4:
        stems.append(word[:-3])
        stems.append(word[:-3] + "e")
        plain = undoubled(word[:-3])
        if plain is not None:
            stems.append(plain)
            stems.append(plain + "e")
    if word.endswith("ment") and len(word) > 6:
        stems.append(word[:-4])
    if word.endswith("al") and len(word) > 4:
        stems.append(word[:-2])
    if word.endswith("ive") and len(word) > 4:
        stems.append(word[:-3])
        stems.append(word[:-3] + "e")
    if word.endswith("ous") and len(word) > 4:
        stems.append(word[:-3])
        stems.append(word[:-3] + "e")
        if word[:-3].endswith("i"):
            stems.append(word[:-4] + "y")
    if word.endswith("dom") and len(word) > 6:
        stems.append(word[:-3])
    if word.endswith("hood") and len(word) > 6:
        stems.append(word[:-4])
    if word.endswith("ation") and len(word) > 6:
        stems.append(word[:-5])
        stems.append(word[:-5] + "ate")
        stems.append(word[:-4])
        stems.append(word[:-4] + "e")
    elif word.endswith("tion") and len(word) > 6:
        stems.append(word[:-4])
        stems.append(word[:-4] + "e")
        stems.append(word[:-3])
    if word.endswith("sion") and len(word) > 6:
        stems.append(word[:-4])
        stems.append(word[:-4] + "e")
    if word.endswith("ance") and len(word) > 6:
        stems.append(word[:-4])
        stems.append(word[:-4] + "e")
    if word.endswith("ence") and len(word) > 6:
        stems.append(word[:-4])
        stems.append(word[:-4] + "e")
    if word.endswith("ibility") and len(word) > 8:
        stems.append(word[:-7] + "ible")
    if word.endswith("ity") and len(word) > 5:
        stems.append(word[:-3])
        stems.append(word[:-3] + "e")
        if word[:-3].endswith("i"):
            stems.append(word[:-4] + "y")
    if word.endswith("ize") and len(word) > 5:
        stems.append(word[:-3])
        stems.append(word[:-3] + "e")
    if word.endswith("ify") and len(word) > 5:
        stems.append(word[:-3])
        stems.append(word[:-3] + "e")
    if word.endswith("ist") and len(word) > 5:
        stems.append(word[:-3])
    if word.endswith("ism") and len(word) > 5:
        stems.append(word[:-3])
    if word.endswith("ability") and len(word) > 8:
        if word[:-7] not in ible_bases \
                and word[:-7] + "e" not in ible_bases:
            stems.append(word[:-7] + "able")
            stems.append(word[:-7] + "ible")
    if word.endswith("ible") and len(word) > 5:
        if word[:-4] not in able_bases \
                and word[:-4] + "e" not in able_bases:
            stems.append(word[:-4])
            stems.append(word[:-4] + "e")
    if word.endswith("able") and len(word) > 5:
        if word[:-4] not in ible_bases \
                and word[:-4] + "e" not in ible_bases:
            stems.append(word[:-4])
            stems.append(word[:-4] + "e")
    if word.endswith("ed") and len(word) > 3:
        ed_stems = [word[:-2], word[:-1]]
        plain = undoubled(word[:-2])
        if plain is not None:
            ed_stems.append(plain)
        if word[:-2].endswith("i"):
            ed_stems.append(word[:-3] + "y")
        if word[:-2] in no_ed_past or word[:-1] in no_ed_past:
            ed_stems = []
        for ed_stem in ed_stems:
            if ed_stem not in no_ed_past:
                stems.append(ed_stem)
    if word.endswith("ing") and len(word) > 4:
        stems.append(word[:-3])
        stems.append(word[:-3] + "e")
        plain = undoubled(word[:-3])
        if plain is not None:
            stems.append(plain)
        if word[:-3].endswith("y"):
            stems.append(word[:-4] + "ie")
    if word.endswith("ly") and len(word) > 3:
        stems.append(word[:-2])
        stems.append(word[:-2] + "e")
        if word[:-2].endswith("i"):
            stems.append(word[:-3] + "y")
    if word.endswith("er") and len(word) > 4:
        if word[:-1] not in no_gradable:
            stems.append(word[:-1])
        plain_cut = word[:-2]
        if plain_cut not in no_gradable \
                and not plain_cut.endswith("e") \
                and not short_single_vowel_cvc(plain_cut):
            stems.append(plain_cut)
        plain = undoubled(word[:-2])
        if plain is not None and plain not in no_gradable:
            stems.append(plain)
        if word[:-2].endswith("i"):
            if word[:-3] + "y" not in no_gradable:
                stems.append(word[:-3] + "y")
    if word.endswith("est") and len(word) > 5:
        plain_cut = word[:-3]
        if plain_cut not in no_gradable \
                and not short_single_vowel_cvc(plain_cut):
            stems.append(plain_cut)
        if word[:-2] not in no_gradable:
            stems.append(word[:-2])
        plain = undoubled(word[:-3])
        if plain is not None and plain not in no_gradable:
            stems.append(plain)
        if word[:-3].endswith("i"):
            if word[:-4] + "y" not in no_gradable:
                stems.append(word[:-4] + "y")
    if word.endswith("y") and len(word) > 3:
        if word[:-1] not in no_y_derivation \
                and not short_single_vowel_cvc(word[:-1]):
            stems.append(word[:-1])
        if word[:-1] + "e" not in no_y_derivation:
            stems.append(word[:-1] + "e")
        plain = undoubled(word[:-1])
        if plain is not None and plain not in no_y_derivation:
            stems.append(plain)
        if len(word[:-1]) >= 4:
            swapped = word[:-3] + word[-2] + word[-3]
            stems.append(swapped)
    return stems


def _is_readable_word(word):
    """Return True only where a letter string stands as a readable
    word on the stated reading: the string stands as a word of
    the language, in the stated lexicon this module carries, in
    its plain form or as a regular inflection of a lexicon form,
    and it carries at least three letters. A string that merely
    has the letter shape of a word, one vowel, one consonant, and
    two distinct letters, does not meet the reading: invented
    pronounceable strings have that shape and stand in no
    lexicon of the language, so they count as no word. The
    charge behind this reading stands in the Round 2 register
    rows R2-035 and R2-055, that a plain word counts only where
    the letter string stands as a readable word, and in the
    plain sentence duty of the design brief at Shape 15. A
    closed compound counts where it divides into parts that
    each stand as a readable word on this same reading, in
    plain form or as a regular inflection or derivation of a
    lexicon form or as a closed compound itself; a compound
    with a part that stands as no readable word counts as no
    word. A derivation carried on a whole compound likewise
    counts where the stem it yields stands as a readable word
    on this reading. A spelling that stands as the barred
    plural of a base whose plural stands in no s form counts
    as no word on the compound reading either, save the two
    spellings the R14-033 bound carries in their exact form,
    informationes and informations, which stand not charged."""
    memo = {}

    # Bases whose plural stands in no s form at all, in the
    # form _readable_stem states for its own limbs. A spelling
    # that stands as the barred plural of one of these bases
    # counts as no word on the compound reading either, the
    # posture row R16-053 charges at informationies, save the
    # two spellings the R14-033 bound carries in their exact
    # form, informationes and informations, which stand not
    # charged and keep the compound reading the bound states.
    no_s_plural = frozenset(
        ("child", "man", "woman", "sheep", "tooth", "wife",
         "mouse", "foot", "leaf", "life", "half", "shelf",
         "children", "data", "information"))
    bound_compound_forms = frozenset(
        ("informationes", "informations"))

    def barred_compound_head(stem):
        # A truncated stem standing as a readable compound
        # whose head, its final part, is a base whose plural
        # stands in no s form stands as the barred plural of
        # that compound head, in the same posture as the bare
        # bases. The information head stands exempt, in the
        # exact bound form the R14-033 bound carries.
        for base in no_s_plural:
            if base == "information":
                continue
            if stem.endswith(base) and len(stem) > len(base):
                if readable(stem[:-len(base)]):
                    return True
        return False

    def barred_plural_form(candidate):
        if candidate.endswith("ies") and len(candidate) > 4:
            return candidate[:-3] in no_s_plural \
                or candidate[:-3] + "e" in no_s_plural
        if candidate.endswith("es") and len(candidate) > 3:
            return candidate[:-2] in no_s_plural \
                or barred_compound_head(candidate[:-2])
        if candidate.endswith("s") and len(candidate) > 3:
            return candidate[:-1] in no_s_plural \
                or barred_compound_head(candidate[:-1])
        return False

    def readable(candidate):
        if candidate in memo:
            return memo[candidate]
        memo[candidate] = False
        result = False
        if len(candidate) >= 3:
            if (candidate.endswith("able") and len(candidate) > 5
                    and (candidate[:-4] in _IBLE_BASES
                         or candidate[:-4] + "e" in _IBLE_BASES)) \
                    or (candidate.endswith("ible")
                        and len(candidate) > 5
                        and (candidate[:-4] in _ABLE_BASES
                             or candidate[:-4] + "e" in _ABLE_BASES)) \
                    or (candidate.endswith("ability")
                        and len(candidate) > 8
                        and (candidate[:-7] in _IBLE_BASES
                             or candidate[:-7] + "e" in _IBLE_BASES)):
                memo[candidate] = False
                return False
            if candidate in _READABLE_LEXICON:
                result = True
            elif any(stem in _READABLE_LEXICON or readable(stem)
                     for stem in _readable_stem(candidate)):
                result = True
            elif barred_plural_form(candidate) \
                    and candidate not in bound_compound_forms:
                result = False
            else:
                def compound_part(part):
                    if len(part) == 2:
                        return part in _READABLE_LEXICON
                    return readable(part)

                # The split search runs as a segmentation over
                # the candidate positions, each part standing at
                # most forty letters, so a long token no split
                # fits is answered from the positions table in
                # time that grows with the token length and the
                # part bound, and not by re-reading every split
                # of every part. A part longer than the bound
                # counts only where it itself segments into
                # parts inside the bound, which the table states.
                part_bound = 40
                size = len(candidate)
                can = [False] * (size + 1)
                can[size] = True
                for start in range(size - 2, -1, -1):
                    for end in range(
                            start + 2,
                            min(size, start + part_bound) + 1):
                        if can[end] and compound_part(
                                candidate[start:end]):
                            can[start] = True
                            break
                for end in range(2, size - 1):
                    if can[end] and compound_part(candidate[:end]):
                        result = True
                        break
        memo[candidate] = result
        return result

    return readable(word)


def _plain_word_count(text):
    """Count plain words on the readable word reading: each
    distinct readable word in the text counts once, so a sentence
    repeating one word counts that word once, and a letter string
    that stands as no readable word counts not at all."""
    stored = _registry_stored_text(text)
    if stored is not None:
        rendered = stored
    else:
        rendered = _safe_str(text)
    words = re.findall(r"[A-Za-z]+", rendered.lower())
    return len({word for word in words if _is_readable_word(word)})


def _field10_matches_grounds(unit):
    """Return True only where the Field 10 marks stand with the
    grounds the unit other fields state. A unit whose other
    fields state that the result rests on a slash, a vouch lien
    amount, or a vouch release must carry the computed in Parley
    seam value in Field 10, and not the no cross seam effect
    value. A unit whose other fields state that the result rests
    on an anchor scenario must carry that scenario in Field 10
    with the DQ-163 mark, and not the statement that no anchor
    scenario is used. A unit whose other fields state that the
    claim depends on Parley Q1, on Parley Q2, or on Parley Q5
    must carry the DQ-164 mark in Field 10, and not the
    statement that no dependence mark applies. Each ground is
    read in the plural and variant wordings the unit may state
    it in, hyphenated, verb, reversed, and spelled out forms
    included, beside its exact singular form."""
    field10 = _part_text(
        dict.get(unit, "qualifiers_and_markings_block")
    ).lower().replace("_", " ")
    other = " ".join(
        _part_text(dict.get(unit, field))
        for field in HEADLINE_UNIT_FIELDS
        if field != "qualifiers_and_markings_block"
    ).lower().replace("_", " ")
    if _seam_ground_stated(other):
        if "computed in parley and not settled in the chosen escrow" \
                not in field10:
            return False
        if "no cross seam effect" in field10:
            return False
    if _anchor_ground_stated(other):
        if "no anchor scenario is used" in field10:
            return False
        if "dq-163" not in field10:
            return False
        for scenario in re.findall(r"\ban-[0-9]+\b", other):
            if scenario not in field10:
                return False
    if _parley_grounds_stated(other):
        if "dq-164" not in field10:
            return False
        if "no dependence mark applies" in field10:
            return False
    return True


def _ground_tokens(text):
    """Return the word tokens of a grounds text, with hyphen and
    underscore separators read as spacing, so a ground stated in
    a hyphenated wording stands in the same tokens as the same
    ground stated with spaces."""
    return re.findall(r"[a-z0-9]+", text.replace("-", " "))


def _seam_ground_stated(other):
    """Return True where the other fields state a seam ground in
    any of its wordings: a vouch release or a vouch lien, in the
    singular or the plural, hyphenated, or stated in a verb form
    such as a vouch that was released, in reversed word order
    such as a release of a vouch or vouches released, in a verb
    head form such as a vouched release or vouching releases,
    with the release word standing before the vouch word or
    further along the same statement than a short window
    reaches, or a slash, stated as slash, slashes, or a slashed
    amount. The vouch head word and the release or lien word
    count as one stated ground where they stand together in
    the unit, in either order, whether they stand in one
    statement or across a statement boundary."""
    tokens = _ground_tokens(other)
    if any(token in ("slash", "slashes", "slashed", "slashing")
           for token in tokens):
        return True
    head_words = ("vouch", "vouches", "vouched", "vouching")
    tail_words = ("release", "releases", "released", "releasing",
                  "lien", "liens")
    if any(token in head_words for token in tokens) \
            and any(token in tail_words for token in tokens):
        return True
    return False


def _anchor_ground_stated(other):
    """Return True where the other fields state an anchor ground
    in any of its wordings: an anchor scenario or anchor
    scenarios, anchors scenarios with the plural head word,
    hyphenated or not, the verb wording anchored in a named
    scenario, the joined wording anchorscenario, the reversed
    joined wording scenarioanchor, the reversed joined test
    wording testanchor, the reversed wordings that
    name the scenario before its anchor, or the anchor test
    and anchor testing wordings the sources prove beside it.
    The scenario or test word counts wherever in the statement
    it stands in relation to the head word, in either word
    order, at any token distance."""
    tokens = _ground_tokens(other)
    if any(token in ("anchorscenario", "anchorscenarios",
                     "anchortest", "anchortests", "anchortesting",
                     "scenarioanchor", "scenariosanchor",
                     "testanchor", "testanchors")
           for token in tokens):
        return True
    if any(token in ("anchor", "anchors", "anchored", "anchoring")
           for token in tokens) \
            and any(word in ("scenario", "scenarios", "test",
                             "tests", "testing")
                    for word in tokens):
        return True
    return False


_PARLEY_GROUND_NUMBERS = {
    "1": "1", "one": "1",
    "2": "2", "two": "2",
    "5": "5", "five": "5",
}


_PARLEY_PIECES = (
    "questions", "question", "parleys", "parley", "numbered",
    "number", "first", "second", "fifth", "five", "1st", "2nd",
    "5th", "one", "two", "q", "1", "2", "5")


def _expand_parley_token(token):
    """Split one joined grounds token into its Parley pieces,
    where the whole token segments into known grounds pieces:
    the name in singular or plural form, the question or q
    limb, an ordinal, and a ground number, in any order. A
    token that does not segment whole stands as itself."""
    if token in _PARLEY_PIECES:
        return [token]

    def segment(rest):
        if not rest:
            return []
        for piece in _PARLEY_PIECES:
            if rest.startswith(piece):
                tail = segment(rest[len(piece):])
                if tail is not None:
                    return [piece] + tail
        return None

    pieces = segment(token)
    if pieces is not None and len(pieces) > 1:
        return pieces
    return [token]


def _parley_grounds_stated(other):
    """Return the set of Parley dependence grounds, among Q1, Q2,
    and Q5, that the other fields state, in any of their
    wordings: Parley Q1 with the letter and number spaced,
    hyphenated, or joined in one word as ParleyQ2, Parley
    question 1 with the number digit or spelled out as a word,
    Parley questions two and five with the plural head word,
    and the reversed wording that names the question before
    Parley. The ordinal wording that numbers the question in
    ordinal words beside the Parley name, the question number
    wording that states the word number before the number
    word, and the reversed wording that names the questions
    and their numbers before the Parley name stand read
    beside those forms. The numbered wording that states the
    word numbered before the number word, the wording that
    states the numbers after the Parley name, and the ordinal
    wording wherever the ordinal word, the question word, and
    the Parley name stand together in the statement stand
    read beside those forms. The spaced Q form, the question
    number form, and the numbered form stand read wherever
    in the statement they stand, at any token distance from
    the Parley name and from the question word. The wording
    that states the number word before the question word, or
    before the Parley name where the question word follows
    the name, stands read beside those forms. The reversed
    joined forms, with the question limb or the number limb
    standing before the Parley name in one joined word, and
    the forms with the number limb standing after the Parley
    name in one joined word, stand read beside the forward
    joined forms. A ground number standing before the q
    token, spaced, joined to the q, or standing after the
    Parley name beside a following q, stands read beside
    the forms that state the number after the q. A ground
    number standing spaced before a single qparley token,
    and a number standing spaced beside a parleyq token,
    stand read beside those forms. A token that joins the
    Parley name to its number limb, with the question or q
    limb standing spaced beside that token, and a token
    that joins the question limb to the Parley name, with
    the number standing spaced before that token, stand
    read beside those forms. The Parley name the number
    before q limbs require stands counted where it stands
    inside a joined token of the statement, not only where
    a standalone parley token stands among the tokens. The
    spaced q limb stands read beside a Parley name token
    that is plural or larger, the joined suffixed ordinal
    stands read after the q limb, the joined ordinal stands
    read before the Parley name with the q limb after the
    name, and the numbered wording stands read with no
    question or q limb in the statement. The ordinal fused
    before the Parley name with the question word standing
    after it, in one token or with the q or question limb
    standing spaced beside that token, the ordinal fused
    before the question word and the Parley name in one
    token, the Parley name fused before the ordinal and the
    question word in one token, the plural Parley name fused
    to the q limb and its number, the ordinal standing spaced
    before a fused parleyq or parleyquestion token, and the
    fused name and question token standing beside a spaced
    number stand read beside those forms."""
    tokens = []
    for raw_token in _ground_tokens(other):
        for piece in _expand_parley_token(raw_token):
            if piece == "parleys":
                piece = "parley"
            if piece == "questions":
                piece = "question"
            tokens.append(piece)
    grounds = set()
    ordinal_numbers = {
        "first": "1", "second": "2", "fifth": "5",
        "1st": "1", "2nd": "2", "5th": "5",
    }
    for index, token in enumerate(tokens):
        if token in ordinal_numbers:
            window = tokens[max(0, index - 3):index + 4]
            if "parley" in window and any(
                    word in ("question", "questions", "q")
                    for word in window):
                grounds.add(ordinal_numbers[token])
        if token in ("question", "questions"):
            following = tokens[index + 1:index + 7]
            if "parley" in following:
                for item in following:
                    if item == "parley":
                        break
                    if item in _PARLEY_GROUND_NUMBERS:
                        grounds.add(
                            _PARLEY_GROUND_NUMBERS[item])
                    if item in ordinal_numbers:
                        grounds.add(ordinal_numbers[item])
                    if item in ("q1", "q2", "q5"):
                        grounds.add(item[1])
            if index + 2 < len(tokens) \
                    and tokens[index + 1] == "number" \
                    and tokens[index + 2] in _PARLEY_GROUND_NUMBERS:
                window = tokens[max(0, index - 4):index + 5]
                if "parley" in window:
                    grounds.add(_PARLEY_GROUND_NUMBERS[
                        tokens[index + 2]])
    for token in tokens:
        joined = re.fullmatch(
            r"parleyq([125])", token)
        if joined is not None:
            grounds.add(joined.group(1))
        plural_name_q = re.fullmatch(
            r"parleysq([125])", token)
        if plural_name_q is not None:
            grounds.add(plural_name_q.group(1))
        joined_word = re.fullmatch(
            r"parleyq(one|two|five)", token)
        if joined_word is not None:
            grounds.add(_PARLEY_GROUND_NUMBERS[joined_word.group(1)])
        joined_question = re.fullmatch(
            r"parleyquestions?([125])", token)
        if joined_question is not None:
            grounds.add(joined_question.group(1))
        joined_question_word = re.fullmatch(
            r"parleyquestions?(one|two|five)", token)
        if joined_question_word is not None:
            grounds.add(
                _PARLEY_GROUND_NUMBERS[joined_question_word.group(1)])
        reversed_joined = re.fullmatch(
            r"(?:questions?|q)([125])parley", token)
        if reversed_joined is not None:
            grounds.add(reversed_joined.group(1))
        reversed_joined_word = re.fullmatch(
            r"(?:questions?|q)(one|two|five)parley", token)
        if reversed_joined_word is not None:
            grounds.add(
                _PARLEY_GROUND_NUMBERS[reversed_joined_word.group(1)])
        number_first_joined = re.fullmatch(
            r"([125]|one|two|five)(?:questions?|q)parley", token)
        if number_first_joined is not None:
            grounds.add(_PARLEY_GROUND_NUMBERS[
                number_first_joined.group(1)])
        parley_number_q = re.fullmatch(
            r"parley([125]|one|two|five)q", token)
        if parley_number_q is not None:
            grounds.add(
                _PARLEY_GROUND_NUMBERS[parley_number_q.group(1)])
        parley_number_questions = re.fullmatch(
            r"parley([125]|one|two|five)questions?", token)
        if parley_number_questions is not None:
            grounds.add(_PARLEY_GROUND_NUMBERS[
                parley_number_questions.group(1)])
        number_parley_questions = re.fullmatch(
            r"([125]|one|two|five)parleyquestions?", token)
        if number_parley_questions is not None:
            grounds.add(_PARLEY_GROUND_NUMBERS[
                number_parley_questions.group(1)])
        q_parley_number = re.fullmatch(
            r"(?:questions?|q)parley([125]|one|two|five)", token)
        if q_parley_number is not None:
            grounds.add(_PARLEY_GROUND_NUMBERS[
                q_parley_number.group(1)])
        number_parley_q = re.fullmatch(
            r"([125]|one|two|five)parleyq", token)
        if number_parley_q is not None:
            grounds.add(_PARLEY_GROUND_NUMBERS[
                number_parley_q.group(1)])
        ordinal_word = (
            r"(first|second|fifth|1st|2nd|5th)")
        for ordinal_pattern in (
                r"parleyquestions?" + ordinal_word,
                r"questions?" + ordinal_word + r"parley",
                r"parley" + ordinal_word + r"q",
                r"parleyq" + ordinal_word,
                ordinal_word + r"qparley",
                ordinal_word + r"parleyq",
                ordinal_word + r"parleyquestions?",
                ordinal_word + r"questions?parley",
                r"parley" + ordinal_word + r"questions?",
                r"q" + ordinal_word + r"parley"):
            ordinal_joined = re.fullmatch(ordinal_pattern, token)
            if ordinal_joined is not None:
                grounds.add(ordinal_numbers[
                    ordinal_joined.group(1)])
        if "parley" in tokens:
            question_number_token = re.fullmatch(
                r"questions?([125]|one|two|five)", token)
            if question_number_token is not None:
                grounds.add(_PARLEY_GROUND_NUMBERS[
                    question_number_token.group(1)])
            number_question_token = re.fullmatch(
                r"([125]|one|two|five)questions?", token)
            if number_question_token is not None:
                grounds.add(_PARLEY_GROUND_NUMBERS[
                    number_question_token.group(1)])
            number_q_token = re.fullmatch(
                r"([125]|one|two|five)q", token)
            if number_q_token is not None:
                grounds.add(_PARLEY_GROUND_NUMBERS[
                    number_q_token.group(1)])
            q_number_token = re.fullmatch(
                r"q([125]|one|two|five)", token)
            if q_number_token is not None:
                grounds.add(_PARLEY_GROUND_NUMBERS[
                    q_number_token.group(1)])
            q_ordinal_token = re.fullmatch(
                r"q(1st|2nd|5th)", token)
            if q_ordinal_token is not None:
                grounds.add(ordinal_numbers[
                    q_ordinal_token.group(1)])
    if "parley" in tokens:
        for index, token in enumerate(tokens):
            if token in _PARLEY_GROUND_NUMBERS \
                    and index + 1 < len(tokens) \
                    and tokens[index + 1] == "q":
                grounds.add(_PARLEY_GROUND_NUMBERS[token])
    for index, token in enumerate(tokens):
        if token != "parley":
            continue
        window = tokens[max(0, index - 4):index + 5]
        for place, item in enumerate(window):
            if item in ("q1", "q2", "q5"):
                grounds.add(item[1])
            if item == "q" and place + 1 < len(window) \
                    and window[place + 1] in _PARLEY_GROUND_NUMBERS:
                grounds.add(_PARLEY_GROUND_NUMBERS[window[place + 1]])
            if item in ("question", "questions") \
                    and place + 1 < len(window) \
                    and window[place + 1] in _PARLEY_GROUND_NUMBERS:
                grounds.add(_PARLEY_GROUND_NUMBERS[window[place + 1]])
    if "parley" in tokens and any(
            word in ("question", "questions") for word in tokens):
        for index, token in enumerate(tokens):
            if token in ordinal_numbers:
                grounds.add(ordinal_numbers[token])
            if token == "numbered" and index + 1 < len(tokens) \
                    and tokens[index + 1] in _PARLEY_GROUND_NUMBERS:
                grounds.add(
                    _PARLEY_GROUND_NUMBERS[tokens[index + 1]])
    for index, token in enumerate(tokens):
        if token != "parley":
            continue
        rest = tokens[index + 1:]
        for place, item in enumerate(rest):
            if item not in ("number", "numbers"):
                continue
            for later in rest[place + 1:]:
                if later in _PARLEY_GROUND_NUMBERS:
                    grounds.add(_PARLEY_GROUND_NUMBERS[later])
                if later in ordinal_numbers:
                    grounds.add(ordinal_numbers[later])
    if "parley" in tokens:
        for index, token in enumerate(tokens):
            if token in ("q1", "q2", "q5"):
                grounds.add(token[1])
            if token == "q" and index + 1 < len(tokens) \
                    and tokens[index + 1] in _PARLEY_GROUND_NUMBERS:
                grounds.add(
                    _PARLEY_GROUND_NUMBERS[tokens[index + 1]])
    if "parley" in tokens and any(
            word in ("question", "questions") for word in tokens):
        for index, token in enumerate(tokens):
            if token in ("question", "questions"):
                for later in tokens[index + 1:]:
                    if later in _PARLEY_GROUND_NUMBERS:
                        grounds.add(
                            _PARLEY_GROUND_NUMBERS[later])
                    if later in ordinal_numbers:
                        grounds.add(ordinal_numbers[later])
            if token == "numbered":
                for later in tokens[index + 1:]:
                    if later in _PARLEY_GROUND_NUMBERS:
                        grounds.add(
                            _PARLEY_GROUND_NUMBERS[later])
    if "parley" in tokens and any(
            word in ("question", "questions") for word in tokens):
        question_places = [
            place for place, word in enumerate(tokens)
            if word in ("question", "questions")]
        parley_places = [
            place for place, word in enumerate(tokens)
            if word == "parley" and any(
                place < question_place
                for question_place in question_places)]
        for index, token in enumerate(tokens):
            if token not in _PARLEY_GROUND_NUMBERS:
                continue
            if any(index < question_place
                   for question_place in question_places):
                grounds.add(_PARLEY_GROUND_NUMBERS[token])
            if any(index < parley_place
                   for parley_place in parley_places):
                grounds.add(_PARLEY_GROUND_NUMBERS[token])
    parley_named = any("parley" in token for token in tokens)
    if parley_named:
        for token in tokens:
            widened_number_q = re.fullmatch(
                r"([125]|one|two|five)q", token)
            if widened_number_q is not None:
                grounds.add(_PARLEY_GROUND_NUMBERS[
                    widened_number_q.group(1)])
            widened_q_number = re.fullmatch(
                r"q([125]|one|two|five)", token)
            if widened_q_number is not None:
                grounds.add(_PARLEY_GROUND_NUMBERS[
                    widened_q_number.group(1)])
            widened_q_ordinal = re.fullmatch(
                r"q(1st|2nd|5th)", token)
            if widened_q_ordinal is not None:
                grounds.add(ordinal_numbers[
                    widened_q_ordinal.group(1)])
        for index, token in enumerate(tokens):
            if token in _PARLEY_GROUND_NUMBERS \
                    and index + 1 < len(tokens) \
                    and tokens[index + 1] == "q":
                grounds.add(_PARLEY_GROUND_NUMBERS[token])
        for index, token in enumerate(tokens):
            if token == "q" and index + 1 < len(tokens):
                following = tokens[index + 1]
                if following in _PARLEY_GROUND_NUMBERS:
                    grounds.add(
                        _PARLEY_GROUND_NUMBERS[following])
                if following in ordinal_numbers:
                    grounds.add(ordinal_numbers[following])
            if token == "numbered" and index + 1 < len(tokens):
                following = tokens[index + 1]
                if following in _PARLEY_GROUND_NUMBERS:
                    grounds.add(
                        _PARLEY_GROUND_NUMBERS[following])
                if following in ordinal_numbers:
                    grounds.add(ordinal_numbers[following])
    for index, token in enumerate(tokens):
        if token in _PARLEY_GROUND_NUMBERS \
                and index + 1 < len(tokens) \
                and tokens[index + 1] in ("qparley", "parleyq"):
            grounds.add(_PARLEY_GROUND_NUMBERS[token])
        if token == "parleyq" and index + 1 < len(tokens) \
                and tokens[index + 1] in _PARLEY_GROUND_NUMBERS:
            grounds.add(
                _PARLEY_GROUND_NUMBERS[tokens[index + 1]])
    question_words = ("question", "questions", "q")
    for index, token in enumerate(tokens):
        before = tokens[index - 1] if index > 0 else None
        after = tokens[index + 1] \
            if index + 1 < len(tokens) else None
        joined_number_parley = re.fullmatch(
            r"([125]|one|two|five)parley", token)
        if joined_number_parley is not None \
                and (before in question_words
                     or after in question_words):
            grounds.add(_PARLEY_GROUND_NUMBERS[
                joined_number_parley.group(1)])
        parley_number_token = re.fullmatch(
            r"parley([125]|one|two|five)", token)
        if parley_number_token is not None \
                and (before in question_words
                     or after in question_words):
            grounds.add(_PARLEY_GROUND_NUMBERS[
                parley_number_token.group(1)])
        if re.fullmatch(r"(?:questions?|q)parley", token) \
                is not None and before in _PARLEY_GROUND_NUMBERS:
            grounds.add(_PARLEY_GROUND_NUMBERS[before])
    for index in range(len(tokens) - 2):
        first, second, third = tokens[index:index + 3]
        if first in ("q", "question", "questions") \
                and second == "parley" \
                and third in _PARLEY_GROUND_NUMBERS:
            grounds.add(_PARLEY_GROUND_NUMBERS[third])
        if first in _PARLEY_GROUND_NUMBERS \
                and second == "parley" and third == "q":
            grounds.add(_PARLEY_GROUND_NUMBERS[first])
    for index in range(len(tokens) - 1):
        if tokens[index] in (
                "qparley", "questionparley", "questionsparley") \
                and tokens[index + 1] in _PARLEY_GROUND_NUMBERS:
            grounds.add(
                _PARLEY_GROUND_NUMBERS[tokens[index + 1]])
    if any("parley" in token for token in tokens):
        for index, token in enumerate(tokens):
            if token in ("question", "questions") \
                    and index + 1 < len(tokens) \
                    and tokens[index + 1] in _PARLEY_GROUND_NUMBERS:
                grounds.add(_PARLEY_GROUND_NUMBERS[
                    tokens[index + 1]])
    for index in range(len(tokens) - 1):
        first, second = tokens[index], tokens[index + 1]
        ordinal_parley_token = re.fullmatch(
            r"(first|second|fifth|1st|2nd|5th)parley", first)
        if ordinal_parley_token is not None \
                and second in ("q", "question", "questions"):
            grounds.add(ordinal_numbers[
                ordinal_parley_token.group(1)])
        if first in ordinal_numbers \
                and second in ("parleyq", "parleyquestion",
                               "parleyquestions"):
            grounds.add(ordinal_numbers[first])
        if first in ("parleyquestion", "parleyquestions") \
                and second in _PARLEY_GROUND_NUMBERS:
            grounds.add(_PARLEY_GROUND_NUMBERS[second])
    if "parley" in tokens and "q" in tokens:
        for token in tokens:
            if token in ordinal_numbers:
                grounds.add(ordinal_numbers[token])
    return grounds


def _has_plain_scope_limits_sentence(value):
    """Return True only where a text part carries a plain scope
    and limits sentence: a sentence in readable words, not code
    only text, that names a scope and states a limit. The scope
    words and the limit words are tested as whole words, never
    as substrings, so the letters of a limit word standing
    inside a longer word state no limit."""
    text = _part_text(value)
    if not isinstance(text, str) or not text.strip():
        return False
    scope_words = ("scope", "sampled", "range", "points", "applies",
                   "covers", "within")
    limit_words = ("limit", "limits", "only", "beyond", "nothing",
                   "not claimed", "no claim")
    for sentence in re.split(r"[.!?]", text):
        lowered = sentence.lower()
        if _plain_word_count(sentence) < 6:
            continue
        if not any(re.search(r"\b" + re.escape(word) + r"\b", lowered)
                   for word in scope_words):
            continue
        if not any(re.search(r"\b" + re.escape(word) + r"\b", lowered)
                   for word in limit_words):
            continue
        return True
    return False


def _is_code_only_text(text):
    """Return True where a text stands as code only: it carries
    fewer plain words than a readable sentence needs."""
    if not isinstance(text, str):
        return True
    sentence = str(text).split(".", 1)[0]
    return _plain_word_count(sentence) < _PLAIN_WORDS_MIN


def validate_headline_unit(unit):
    """Return True only for a closed unit in the fixed field
    order, carrying its assumption set, its rows, its range kind,
    and every dependence mark as part of the unit itself. The
    centre only fixture unit never validates as a headline unit,
    and a unit carrying an extra Range kind field fails. The
    envelope parts stand checked on content as well as presence:
    no part may stand empty, in plain form or in the dress of an
    empty container, a dict carrying only empty content, empty
    bytes, a memoryview carrying no bytes content, a part standing
    in a type the check does not read, a zero, or a False, hidden
    as redacted, pointed elsewhere, or stated as none; the claim
    sentence may not claim the result over all points; and a region stated as a
    record must carry its sampled point enumeration, each point
    as axis values in numbers with its outcome in words."""
    if not isinstance(unit, dict):
        return False
    stored_pairs = list(dict.items(unit))
    keys = [key for key, _stored_value in stored_pairs]

    def _field_value(field):
        for stored_key, stored_value in stored_pairs:
            if any(key_text is not None
                   and str.__eq__(key_text, field)
                   for key_text in _registry_key_texts(stored_key)):
                return True, stored_value
        return False, None

    if any(
            not any(
                any(key_text is not None
                    and str.__eq__(key_text, field)
                    for key_text in _registry_key_texts(key))
                for field in HEADLINE_UNIT_FIELDS)
            for key in keys):
        return False
    for field in HEADLINE_UNIT_FIELDS:
        present, field_value = _field_value(field)
        if not present or field_value is None:
            return False
    if len(keys) != len(HEADLINE_UNIT_FIELDS) or not all(
            any(key_text is not None
                and str.__eq__(key_text, field)
                for key_text in _registry_key_texts(key))
            for key, field in zip(keys, HEADLINE_UNIT_FIELDS)):
        return False
    identifier = _field_value(
        "headline_unit_identifier_and_issue_date")[1]
    if isinstance(identifier, str):
        identifier = str.__str__(identifier)
    else:
        try:
            identifier = str(identifier)
        except Exception:
            return False
    if F01_UNIT_MARK in identifier:
        return False
    for field in HEADLINE_UNIT_FIELDS:
        if not _envelope_part_stands(_field_value(field)[1]):
            return False
    for field in ("holding_region", "failure_region"):
        if not _region_stands(_field_value(field)[1]):
            return False
    claim = _field_value("claim_sentence")[1]
    if isinstance(claim, str):
        claim = str.__str__(claim)
    claim = str(claim).lower()
    if "everywhere" in claim or "all points" in claim:
        return False
    if not _field10_stands(
            _field_value("qualifiers_and_markings_block")[1]):
        return False
    grounds_unit = {
        field: _field_value(field)[1]
        for field in HEADLINE_UNIT_FIELDS}
    if not _field10_matches_grounds(grounds_unit):
        return False
    if not _has_plain_scope_limits_sentence(
            _field_value("claim_sentence")[1]):
        return False
    if not _has_plain_scope_limits_sentence(
            _field_value("grounding_sentence")[1]):
        return False
    return True


def _quoted_copy(value, _memo=None, _depth=0):
    """Copy a value through base class readings only. Dict parts
    stand read through the base dict items reading, and sequence
    and set parts through their base iteration, so a part that
    overrides items or the copy protocol is quoted as the content
    the base readings show, never as content its own override
    supplies. A part in no container form and no plain scalar
    form stands quoted as itself, so no copy protocol of the
    part itself is ever invoked. The buffer forms stand carried
    as stored: a bytearray as a fresh bytearray and a memoryview
    as a memoryview over fresh bytes. A value nested past the depth
    bound stands refused in named form. The bound counts
    containers only, on the stated basis of R3-056: a chain of
    101 containers over a scalar leaf stands within the bound,
    and a chain of 102 containers stands past it, so the bound
    test stands on a part only where that part is itself a
    container, and a scalar leaf at the foot of a chain of 101
    containers draws no refusal."""
    if _depth > _DEPTH_BOUND and isinstance(
            value, (dict, list, tuple, set, frozenset)):
        raise ValueError(
            "quoted copy stands refused in named form: a value "
            "stands nested past the depth bound")
    if _memo is None:
        _memo = {}
    if isinstance(value, memoryview):
        return memoryview(bytes(value))
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            frozen_key = _quoted_copy(key, _memo, _depth + 1)
            frozen_item = _quoted_copy(item, _memo, _depth + 1)
            try:
                collides = frozen_key in copied
            except Exception:
                collides = False
            if collides:
                counter = 2
                while True:
                    if isinstance(frozen_key, str):
                        distinct_key = (
                            str.__str__(frozen_key)
                            + " (carried key " + str(counter) + ")")
                    else:
                        distinct_key = (frozen_key, counter)
                    try:
                        distinct_taken = distinct_key in copied
                    except Exception:
                        distinct_taken = False
                    if not distinct_taken:
                        frozen_key = distinct_key
                        break
                    counter += 1
            try:
                copied[frozen_key] = frozen_item
            except Exception:
                counter = 2
                while True:
                    if isinstance(frozen_key, str):
                        candidate = (
                            str.__str__(frozen_key)
                            + " (carried key " + str(counter) + ")")
                    elif counter == 2:
                        candidate = (frozen_key, counter)
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
                        copied[candidate] = frozen_item
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
            _quoted_copy(item, _memo, _depth + 1)
            for item in list.__iter__(value))
        return copied
    if isinstance(value, tuple):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = tuple(
            _quoted_copy(item, _memo, _depth + 1)
            for item in tuple.__iter__(value))
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
            carried_items = []
            failed = False
            for item in set.__iter__(value):
                frozen_item = _quoted_copy(item, _memo, _depth + 1)
                carried_items.append(frozen_item)
                if failed:
                    continue
                try:
                    copied.add(frozen_item)
                except Exception:
                    failed = True
            if failed:
                _memo[id(value)] = carried_items
                return carried_items
            return copied
        carried_items = [
            _quoted_copy(item, _memo, _depth + 1)
            for item in frozenset.__iter__(value)]
        try:
            copied = frozenset(carried_items)
        except Exception:
            _memo[id(value)] = carried_items
            return carried_items
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, bytearray):
        return bytearray(bytes(value))
    if isinstance(value, (str, bytes, int, float, complex,
                          bool)) or value is None:
        return value
    return value


def _headline_unit_refusal(unit):
    if not isinstance(unit, dict):
        return (
            "quote_headline_unit stands refused: the headline unit stands "
            "in no record form, a headline unit stands as a field mapping, "
            "and no unit stands quoted")
    stored_pairs = list(dict.items(unit))
    keys = [key for key, _stored_value in stored_pairs]

    def _field_value(field):
        for stored_key, stored_value in stored_pairs:
            if any(key_text is not None
                   and str.__eq__(key_text, field)
                   for key_text in _registry_key_texts(stored_key)):
                return True, stored_value
        return False, None

    extra = [
        key for key in keys
        if not any(
            any(key_text is not None
                and str.__eq__(key_text, field)
                for key_text in _registry_key_texts(key))
            for field in HEADLINE_UNIT_FIELDS)]
    if extra:
        return (
            "quote_headline_unit stands refused: fields beyond the closed "
            "unit: " + ", ".join(_stored_str(key) for key in extra)
            + ", and no unit stands quoted")
    for field in HEADLINE_UNIT_FIELDS:
        present, field_value = _field_value(field)
        if not present or field_value is None:
            return (
                "quote_headline_unit stands refused: headline unit field "
                "absent: " + field + ", and no unit stands quoted")
    if len(keys) != len(HEADLINE_UNIT_FIELDS) or not all(
            any(key_text is not None
                and str.__eq__(key_text, field)
                for key_text in _registry_key_texts(key))
            for key, field in zip(keys, HEADLINE_UNIT_FIELDS)):
        return (
            "quote_headline_unit stands refused: the headline unit fields "
            "stand out of the closed unit order, and no unit stands quoted")
    prefix = "quote_headline_unit stands refused: "
    suffix = ", and no unit stands quoted"
    try:
        identifier = _field_value(
            "headline_unit_identifier_and_issue_date")[1]
        if isinstance(identifier, str) \
                and F01_UNIT_MARK in str.__str__(identifier):
            return (
                prefix + "headline unit field "
                "headline_unit_identifier_and_issue_date carries "
                "the centre only fixture mark" + suffix)
        for field in HEADLINE_UNIT_FIELDS:
            if not _envelope_part_stands(_field_value(field)[1]):
                return (
                    prefix + "headline unit field " + field
                    + " stands empty, hidden, or in no standing "
                    "content form" + suffix)
        for field in ("holding_region", "failure_region"):
            if not _region_stands(_field_value(field)[1]):
                return (
                    prefix + "headline unit field " + field
                    + " does not carry its sampled point "
                    "enumeration in standing form" + suffix)
        claim_value = _field_value("claim_sentence")[1]
        claim_text = claim_value
        if isinstance(claim_text, str):
            claim_text = str.__str__(claim_text)
        claim_lower = str(claim_text).lower()
        if "everywhere" in claim_lower or "all points" in claim_lower:
            return (
                prefix + "headline unit field claim_sentence "
                "claims the result everywhere or over all points"
                + suffix)
        if not _field10_stands(
                _field_value("qualifiers_and_markings_block")[1]):
            return (
                prefix + "headline unit field "
                "qualifiers_and_markings_block does not carry "
                "its stated marks" + suffix)
        if not _field10_matches_grounds(unit):
            return (
                prefix + "headline unit field "
                "qualifiers_and_markings_block does not carry "
                "the mark a ground stated in the unit requires"
                + suffix)
        if not _has_plain_scope_limits_sentence(
                _field_value("claim_sentence")[1]):
            return (
                prefix + "headline unit field claim_sentence "
                "carries no plain scope and limits sentence"
                + suffix)
        if not _has_plain_scope_limits_sentence(
                _field_value("grounding_sentence")[1]):
            return (
                prefix + "headline unit field grounding_sentence "
                "carries no plain scope and limits sentence"
                + suffix)
    except Exception:
        pass
    return (
        "quote_headline_unit stands refused: the headline unit does not "
        "validate as a quotable unit whole, and no unit stands quoted")


def quote_headline_unit(unit):
    """Quote a headline unit whole. A unit that does not validate
    is not quoted at all. The quotation copies the validated unit
    through base class readings only, never through a copy
    protocol a part of the unit overrides. A standing memoryview
    part stands quoted as a memoryview over fresh bytes holding
    the content it carries, so quotation of a standing unit
    never fails in the copy act itself."""
    if not validate_headline_unit(unit):
        raise ValueError(_headline_unit_refusal(unit))
    return _quoted_copy(unit)


def first_sentence(text):
    """Return the first sentence of a claim text, read on the
    text the claim stores where it carries a stored text, and
    through the module safe string form where it carries
    none, never through a string reading the claim itself
    supplies."""
    return _stored_str(text).split(".", 1)[0]


def validate_working_range_claim(text, assumption_set, rows, range_kind):
    """Return True only where the first sentence of a working
    range claim names its assumption set, its rows, and its range
    kind. A first sentence naming none of the three, or only some
    of them, does not meet the claim form."""
    sentence = first_sentence(text)
    if _is_code_only_text(sentence):
        return False
    for named in (assumption_set, rows, range_kind):
        stored = _registry_stored_text(named)
        if stored is not None:
            rendered = stored
        else:
            rendered = ""
        if not rendered:
            return False
        if rendered not in sentence:
            return False
    return True


def moved_reading(delta, reporting_resolution):
    """Decide moved or not moved for one trace: the trace moved
    where its change reaches the reporting resolution for that
    trace stated in the family record before runs. The rule reads
    only the recorded change and the recorded resolution, so a
    second reader applying it to the same record reaches the same
    reading."""
    plain_delta = _plain_number_value(delta)
    plain_resolution = _plain_number_value(reporting_resolution)
    if plain_delta is None or plain_resolution is None:
        raise ValueError(
            "moved_reading stands refused: the change and the "
            "reporting resolution stand in no number form, plain "
            "numbers stand required, and no moved reading stands "
            "returned") from None
    return abs(plain_delta) >= plain_resolution


def validate_bounding_headline(headline, family_record, run_record):
    """Return True only for a bounding headline in full form: it
    carries the external work issuance axis beside farm size and
    patience, it states which of the three traces moved and which
    did not, and it names the zero edge witness shape wherever the
    headline rests on the external work issuance axis or on a farm
    whose internal edge count stands zero or near zero under the
    bound the family record states."""
    if not isinstance(headline, dict):
        return False
    axes_value = dict.get(headline, "axes") or ()
    if isinstance(axes_value, (list, tuple, set, frozenset)):
        axes_value = tuple(_base_iter(axes_value))
    else:
        axes_value = ()
    if len(axes_value) != len(AXES) or not all(
            isinstance(element, str)
            and str.__eq__(str.__str__(element), stated)
            for element, stated in zip(axes_value, AXES)):
        return False
    traces = dict.get(headline, "traces") or []
    if isinstance(traces, (list, tuple)):
        if (list.__len__(traces) if isinstance(traces, list) else tuple.__len__(traces)) != 3:
            return False
        traces = list(_base_iter(traces))
    else:
        return False
    for trace in traces:
        if not isinstance(trace, dict) or not dict.__contains__(trace, "moved"):
            return False
    needs_witness = _registry_text_equals(
        dict.get(headline, "rests_on_axis"),
        "external work issuance")
    edge_count = dict.get(run_record, "farm_internal_edge_count") if isinstance(run_record, dict) else None
    bound = dict.get(family_record, "near_zero_bound") if isinstance(family_record, dict) else None
    if edge_count is not None and bound is not None:
        plain_edge = _plain_number_value(edge_count)
        plain_bound = _plain_number_value(bound)
        if plain_edge is None or plain_bound is None:
            needs_witness = True
        elif plain_edge <= plain_bound:
            needs_witness = True
    if needs_witness and not dict.get(headline, "zero_edge_witness_shape"):
        return False
    return True


def validate_envelope_claim(claim):
    """Return True only under envelope discipline: the claim
    states what holds at sampled points and over the stated ranges
    only, names a failure witness for what fails, and states
    nothing about values between sampled points."""
    if not isinstance(claim, dict):
        return False
    if dict.__contains__(claim, "holding_region") or dict.__contains__(claim, "claim_sentence"):
        if not validate_headline_unit(claim):
            return False
        if dict.get(claim, "failure_region") and not _region_stands(
                dict.get(claim, "witness_block")):
            return False
        return True
    if not _registry_text_equals(
            dict.get(claim, "scope"),
            "sampled points and stated ranges only"):
        return False
    if dict.get(claim, "claims_between_points"):
        return False
    if dict.get(claim, "monotonicity_claimed") or dict.get(claim, "interpolation_claimed"):
        return False
    if dict.get(claim, "holds") is False and not dict.get(claim, "failure_witness"):
        return False
    return True


def _whole_number_count(value):
    """The whole number a handed count stands as, where the
    count stands in whole number form alone: a plain int, a
    boolean standing apart from every number, through its
    base class reading, so an int subclass stands read on the
    whole number it stores and never through a conversion or
    equality reading it supplies. A count in any other form,
    fractional, text, boolean, Decimal, or Fraction, stands
    in no whole number form here and reads as None."""
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return int.__int__(value)


def _plain_number_value(value):
    """The plain number a handed value stands as, where the
    value stands in the plain number limb, an int or a float
    with a boolean standing apart, read through its base
    class reading, so a number subclass stands judged on the
    number it stores and never through a comparison reading
    it supplies. A value in any other form reads as None."""
    if isinstance(value, bool) \
            or not isinstance(value, (int, float)):
        return None
    if isinstance(value, int):
        return int.__int__(value)
    return float.__float__(value)


def honest_loss_rate_h1(submitted, accepted_by_submission_period):
    """The honest loss rate in the decided H1 form: the period
    subtraction, with each accepted unit attributed to the period
    in which it was submitted. So attributed, the subtraction
    equals the event count by construction and cannot fall below
    zero. The rate travels as a stored numerator and denominator
    pair. A count pair no population can carry stands refused in
    the named whole number form: a negative count on either side,
    an accepted count above the submitted count, or a submitted
    count of zero, which carries no population a rate can stand
    on. No clamp stands applied in silence to any such pair."""
    submitted_count = _whole_number_count(submitted)
    accepted_count = _whole_number_count(
        accepted_by_submission_period)
    if submitted_count is None or accepted_count is None:
        raise ValueError(
            "honest_loss_rate_h1 stands refused: the submitted "
            "and accepted counts stand in no whole number form, "
            "whole numbers stand required, and no loss rate "
            "stands computed") from None
    if submitted_count <= 0 or accepted_count < 0 \
            or accepted_count > submitted_count:
        raise ValueError(
            "honest_loss_rate_h1 stands refused: the submitted "
            "and accepted counts stand as no population can "
            "carry them, a negative count, an accepted count "
            "above the submitted count, or a submitted count "
            "of zero, whole numbers a population can carry "
            "stand required, and no loss rate stands "
            "computed") from None
    return {
        "form": "H1",
        "numerator": submitted_count - accepted_count,
        "denominator": submitted_count,
    }


def top_up_applies(winning_probability):
    """The top up duty at F-18, read with closed bounds: it
    applies at or above 0.1 and at or below 0.9."""
    plain_probability = _plain_number_value(winning_probability)
    if plain_probability is None:
        raise ValueError(
            "top_up_applies stands refused: the winning "
            "probability stands in no number form, a plain "
            "number stands required, and no top up judgement "
            "stands returned") from None
    if isinstance(plain_probability, float) and not math.isfinite(
            plain_probability):
        raise ValueError(
            "top_up_applies stands refused: the winning "
            "probability stands in no finite form, a "
            "probability stands as a finite number from zero "
            "to one, and no top up judgement stands "
            "returned") from None
    if plain_probability < 0 or plain_probability > 1:
        raise ValueError(
            "top_up_applies stands refused: the winning "
            "probability stands outside the closed range "
            "from zero to one, a probability stands inside "
            "that range, and no top up judgement stands "
            "returned") from None
    return 0.1 <= plain_probability <= 0.9


def point_standing(replicate_count):
    """Return the standing of one control point against the 30
    replicate floor, with its count stated. A point below the
    floor borrows no standing of a point at the floor."""
    count = _whole_number_count(replicate_count)
    if count is None:
        raise ValueError(
            "point_standing stands refused: the replicate count "
            "stands in no whole number form, a whole number "
            "stands required, and no point standing stands "
            "returned") from None
    if count < 0:
        raise ValueError(
            "point_standing stands refused: the replicate "
            "count stands negative, a count stands as a whole "
            "number at or above zero, and no point standing "
            "stands returned") from None
    return {
        "replicates": count,
        "standing": "at floor" if count >= 30 else "below floor",
    }


def classify_run_outcome(run_length_in_days, regime_class):
    """Classify one run outcome. A run shorter than 30 simulated
    days is not classifiable as attacker winning under the final
    30 day rule: its outcome stands recorded as horizon
    insufficient and contributes to no transition figure."""
    run_days = _whole_number_count(run_length_in_days)
    if run_days is None:
        raise ValueError(
            "classify_run_outcome stands refused: the run length "
            "in days stands in no whole number form, a whole "
            "number stands required, and no outcome stands "
            "classified") from None
    if run_days < 0:
        raise ValueError(
            "classify_run_outcome stands refused: the run "
            "length in days stands negative, a run length "
            "stands as a whole number of days at or above "
            "zero, and no outcome stands classified") from None
    if run_days < 30:
        return {
            "outcome": "horizon insufficient",
            "contributes_to_transition_figure": False,
        }
    return {
        "outcome": regime_class,
        "contributes_to_transition_figure": True,
    }


def transition_figure(replicates):
    """Compute the transition figure at one control point over all
    replicates started at that point. Every replicate contributes
    exactly one recorded outcome by the horizon: a first terminal
    regime named by its class, or right censoring at the horizon.
    Competing regime exits stand counted as competing events and
    never as censoring. Each replicate stands counted once: a
    replicate handed more than once, the same record in the same
    stored form, contributes one outcome, judged on the content
    form of the record. Over no replicates the figure states no
    share: the right censored share stands as the undelivered
    standing, unknown, that the sibling doors of this estate
    state over no population, and no denominator stands invented
    for it. The denominator rule stands stated in the result."""
    if not isinstance(replicates, (list, tuple, set, frozenset)):
        raise ValueError(
            "transition_figure stands refused: the replicates "
            "stand in no list form, a list of replicate records "
            "stands required, and no transition figure stands "
            "computed")
    stored_replicates = list(_base_iter(replicates))
    for replicate in stored_replicates:
        if not isinstance(replicate, dict):
            raise ValueError(
                "transition_figure stands refused: a replicate "
                "stands in no record form, a replicate stands as "
                "a record, and no transition figure stands "
                "computed")
    counted_replicates = []
    seen_forms = []
    for replicate in stored_replicates:
        form = _form_repr(replicate)
        if form not in seen_forms:
            seen_forms.append(form)
            counted_replicates.append(replicate)
    total = len(counted_replicates)
    counts = {}
    competing = 0
    censored = 0
    for replicate in counted_replicates:
        if dict.get(replicate, "competing_exit") if isinstance(replicate, dict) else replicate.get("competing_exit"):
            competing += 1
            continue
        regime = dict.get(replicate, "first_terminal_regime") if isinstance(replicate, dict) else replicate.get("first_terminal_regime")
        if regime is None:
            censored += 1
        else:
            try:
                hash(regime)
            except Exception:
                raise ValueError(
                    "transition_figure stands refused: a replicate "
                    "first terminal regime stands in no name form, "
                    "a regime name stands required, and no "
                    "transition figure stands computed") from None
            counts[regime] = counts.get(regime, 0) + 1
    denominator = total
    incidence = {
        regime: {"count": count, "denominator": total,
                 "share": count / denominator}
        for regime, count in counts.items()
    }
    return {
        "denominator": total,
        "denominator_rule": (
            "computed over all replicates started at the point, "
            "each replicate counted once; competing regime exits "
            "counted as competing events and never as censoring"),
        "cumulative_incidence": incidence,
        "competing_events": competing,
        "right_censored": {
            "count": censored, "denominator": total,
            "share": (censored / denominator) if total else "unknown",
        },
        "outcomes_per_replicate": 1,
    }


def location_for_endpoint(figure, regime, band_endpoint):
    """Return the location of a band endpoint at a point, or None
    where cumulative incidence by the horizon does not reach the
    endpoint: no location stands reported for that endpoint at
    that point."""
    if not isinstance(figure, dict):
        return None
    incidence = dict.get(figure, "cumulative_incidence") or {}
    try:
        entry = dict.get(incidence, regime) if isinstance(incidence, dict) else None
    except Exception:
        return None
    if entry is None:
        return None
    try:
        share = dict.get(entry, "share") if isinstance(entry, dict) else entry["share"]
    except Exception:
        return None
    plain_share = _plain_number_value(share)
    plain_endpoint = _plain_number_value(band_endpoint)
    if plain_share is None or plain_endpoint is None:
        return None
    if plain_share < plain_endpoint:
        return None
    return {"regime": regime, "endpoint": band_endpoint,
            "share": share}


def record_first_observed(previous_evaluation_day, observed_day,
                          horizon, is_last_day=False):
    """Record the time of a first observed regime condition as the
    interval from the previous daily evaluation to the evaluation
    at which it was first observed, never as an exact event time.
    A condition first seen on the last day of a run has its
    interval closed only by the horizon."""
    close = horizon if is_last_day else observed_day
    return {
        "interval": (previous_evaluation_day, close),
        "form": "interval from previous daily evaluation",
        "exact_event_time": None,
    }


def validate_observation_time(record):
    """Return True only where a first observed regime stands in
    interval form. An exact event time fails."""
    if not isinstance(record, dict):
        return False
    if dict.get(record, "exact_event_time") is not None:
        return False
    interval = dict.get(record, "interval")
    return isinstance(interval, (list, tuple)) and (list.__len__(interval) if isinstance(interval, list) else tuple.__len__(interval)) == 2


def _grid_pair(location, act):
    try:
        if isinstance(location, (str, bytes, dict)):
            raise TypeError("a location stands in no pair form")
        first = location[0]
        second = location[1]
        first_number = _whole_number_count(first)
        second_number = _whole_number_count(second)
        if first_number is None or second_number is None:
            raise TypeError("a location part stands in no grid form")
        return (first_number, second_number)
    except Exception:
        raise ValueError(
            act + " stands refused: a location must stand as a pair of "
            "grid numbers, and the handed location "
            + _form_repr(location) + " stands in no such form") from None


def region_shift_steps(location_a, location_b):
    """Return the shift of a region location between two points,
    in grid steps on each axis."""
    try:
        pair_a = _grid_pair(location_a, "region_shift_steps")
    except (KeyboardInterrupt, SystemExit):
        raise ValueError(
            "region_shift_steps stands refused: a location must "
            "stand as a pair of grid numbers, and the handed "
            "location " + type(location_a).__name__
            + " stands in no such form") from None
    try:
        pair_b = _grid_pair(location_b, "region_shift_steps")
    except (KeyboardInterrupt, SystemExit):
        raise ValueError(
            "region_shift_steps stands refused: a location must "
            "stand as a pair of grid numbers, and the handed "
            "location " + type(location_b).__name__
            + " stands in no such form") from None
    return (
        abs(pair_a[0] - pair_b[0]),
        abs(pair_a[1] - pair_b[1]),
    )


def transition_wording(location_a, location_b, location_reported=None):
    """Return the wording of a stability comparison. A transition
    stands reported as holding only where the region location is
    stable, moving by no more than one grid step on either axis.
    Where the narrowing test fails, the region stands reported as
    a finite population crossover, in those words. Stability is
    tested only where a location stands reported at both points:
    where no location stands reported at a point, the report
    states the crossover form or the censored form and makes no
    holding statement."""
    if location_reported is not None and not all(location_reported):
        return {
            "wording": "censored form",
            "holding_statement": False,
        }
    try:
        shift = region_shift_steps(location_a, location_b)
    except ValueError:
        try:
            pair_a = _grid_pair(location_a, "transition_wording")
        except (KeyboardInterrupt, SystemExit):
            raise ValueError(
                "transition_wording stands refused: a location must "
                "stand as a pair of grid numbers, and the handed "
                "location " + type(location_a).__name__
                + " stands in no such form") from None
        try:
            pair_b = _grid_pair(location_b, "transition_wording")
        except (KeyboardInterrupt, SystemExit):
            raise ValueError(
                "transition_wording stands refused: a location must "
                "stand as a pair of grid numbers, and the handed "
                "location " + type(location_b).__name__
                + " stands in no such form") from None
        shift = (abs(pair_a[0] - pair_b[0]), abs(pair_a[1] - pair_b[1]))
    if shift[0] <= 1 and shift[1] <= 1:
        return {"wording": "holding", "holding_statement": True}
    return {
        "wording": "finite population crossover",
        "holding_statement": False,
    }


def validate_transition_report(report):
    """Return True only for a full transition report: the full
    distribution near the threshold, the three regime class
    counts, the honest loss rate in the H1 form beside the
    headline figure, and at least 30 replicates per control point
    near the threshold, with the top up rule applied and recorded
    where a screening point lands within the closed bounds."""
    if not isinstance(report, dict):
        return False
    try:
        if not dict.get(report, "distribution_near_threshold"):
            return False
        counts = dict.get(report, "regime_class_counts") or {}
        if isinstance(counts, dict):
            counts_len = dict.__len__(counts)
        elif isinstance(counts, list):
            counts_len = list.__len__(counts)
        elif isinstance(counts, tuple):
            counts_len = tuple.__len__(counts)
        else:
            return False
        if counts_len != 3:
            return False
        if isinstance(counts, dict):
            count_entries = list(dict.values(counts))
        else:
            count_entries = list(_base_iter(counts))
        for count_entry in count_entries:
            if _whole_number_count(count_entry) is None:
                return False
        rate = dict.get(report, "honest_loss_rate") or {}
        if not isinstance(rate, dict) or not _registry_text_equals(
                dict.get(rate, "form"), "H1"):
            return False
        points = dict.get(report, "points") or []
        if isinstance(points, (list, tuple, set, frozenset)):
            points = list(_base_iter(points))
        for point in points:
            if not isinstance(point, dict):
                return False
            if _stored_truth_stands(dict.get(point, "near_threshold")):
                replicates = _whole_number_count(
                    dict.get(point, "replicates", 0))
                if replicates is None or replicates < 30:
                    return False
            probability = dict.get(point, "winning_probability")
            if probability is not None and top_up_applies(probability):
                if not dict.get(point, "top_up_recorded"):
                    return False
    except Exception:
        return False
    return True


def validate_transition_unit(unit):
    """Return True only where a transition report unit carries, in
    the same unit as its headline figure, the cumulative incidence
    of each terminal regime class by the stated horizon and the
    share of replicates right censored at that horizon, each
    labelled derived from the replicate counts in that unit, and
    every location sentence names its horizon."""
    if not isinstance(unit, dict):
        return False
    figure = dict.get(unit, "transition_figure") or {}
    if not isinstance(figure, dict):
        return False
    if not dict.get(figure, "cumulative_incidence"):
        return False
    if not dict.__contains__(figure, "right_censored"):
        return False
    if not _registry_text_equals(
            dict.get(unit, "incidence_label"),
            "derived from the replicate counts in this unit"):
        return False
    horizon = dict.get(unit, "horizon")
    if horizon is None:
        horizon = dict.get(figure, "horizon")
    if horizon is None:
        horizon = dict.get(figure, "stated_horizon")
    if horizon is None:
        horizon = dict.get(unit, "stated_horizon")
    plain_horizon = None
    if horizon is not None:
        plain_horizon = _plain_number_value(horizon)
        if plain_horizon is None:
            return False
    sentences = dict.get(unit, "location_sentences") or []
    if isinstance(sentences, (list, tuple, set, frozenset)):
        sentences = list(_base_iter(sentences))
    for sentence in sentences:
        if not isinstance(sentence, str):
            return False
        stored_sentence = str.__str__(sentence)
        if "horizon" not in stored_sentence:
            return False
        numbers = re.findall(r"[0-9]+(?:\.[0-9]+)?", stored_sentence)
        if not numbers:
            return False
        if plain_horizon is not None:
            lowered = stored_sentence.lower()
            positioned = re.findall(
                r"([0-9]+(?:\.[0-9]+)?)\s*(?:days?\s+)?horizon",
                lowered)
            positioned += re.findall(
                r"horizon\s*(?:is\s+|of\s+|:|=)?\s*"
                r"([0-9]+(?:\.[0-9]+)?)",
                lowered)
            if not positioned:
                return False
            if not any(float(value) == plain_horizon
                       for value in positioned):
                return False
    return True


def reporter_inputs_for_family(retained_records):
    """Return the Reporter inputs of one family as carried through
    the retained records at S-10: the divergence count computed at
    S-04 as it stands, or the blocked family mark where it stands,
    naming the affected family and the affected share."""
    records = retained_records if isinstance(retained_records, dict) else {}
    return {
        "divergence_count": _quoted_copy(
            dict.get(records, "divergence_count")),
        "blocked_family_mark": _quoted_copy(
            dict.get(records, "blocked_family_mark")),
    }


def _stored_truth_stands(value):
    """Whether a handed mark field stands, judged on the form
    it stores and never through a truth reading the value
    itself supplies: a boolean on its identity, a plain
    number on its base class reading against zero, a text or
    buffer or container form on its base length, no value as
    not standing, and any other stored object as standing by
    its presence alone."""
    if value is None:
        return False
    if isinstance(value, bool):
        return value is True
    if isinstance(value, int):
        return int.__ne__(value, 0)
    if isinstance(value, float):
        return float.__ne__(value, 0.0)
    if isinstance(value, str):
        return str.__len__(value) > 0
    if isinstance(value, bytes):
        return bytes.__len__(value) > 0
    if isinstance(value, bytearray):
        return bytearray.__len__(value) > 0
    if isinstance(value, dict):
        return dict.__len__(value) > 0
    if isinstance(value, (list, tuple, set, frozenset)):
        return len(list(_base_iter(value))) > 0
    return True


def share_report_stands(inputs, share):
    """Report whether a report may read an affected share as
    standing as reported. The function returns a boolean only: it
    reports the standing of the share for reading, and no caller
    wires it into the headline unit build path. While a blocked
    family mark stands for a share, with its count nonzero and
    unresolved, the function returns False for that share, and it
    returns True otherwise."""
    mark = dict.get(inputs, "blocked_family_mark") if isinstance(inputs, dict) else None
    if isinstance(mark, dict):
        affected_text = _registry_stored_text(
            dict.get(mark, "affected_share"))
        share_text = _registry_stored_text(share)
        if affected_text is not None and share_text is not None \
                and str.__eq__(affected_text, share_text):
            if _stored_truth_stands(dict.get(mark, "count", 0)) \
                    and not _stored_truth_stands(
                        dict.get(mark, "resolved")):
                return False
    return True


def build_headline_unit_from_run(run_id, values, store_kind="sweep",
                                 family_record=None):
    """Build one headline unit from the retained records of one
    run, resolving the run record in one lookup through the
    Recorder store reading path. Where the record does not
    resolve, no unit stands built and the failure stands returned
    as a named failure and recorded in the family record where
    one stands handed in."""
    try:
        record = mod10.store_lookup(store_kinds=(store_kind,), key=run_id)
    except mod10.LookupFailure:
        failure = {
            "name": mod10.ONE_LOOKUP_FAILURE_NAME,
            "run_status": "failed",
            "complete": False,
            "run_identifier": run_id,
        }
        if isinstance(family_record, dict):
            family_record.setdefault("named_failures", []).append(
                _quoted_copy(failure))
        return {"built": False, "failure": failure, "unit": None}
    except Exception as error:
        failure = {
            "name": type(error).__name__ + ": " + _safe_str(error),
            "run_status": "failed",
            "complete": False,
            "run_identifier": run_id,
        }
        if isinstance(family_record, dict):
            family_record.setdefault("named_failures", []).append(
                _quoted_copy(failure))
        return {"built": False, "failure": failure, "unit": None}
    if isinstance(values, dict):
        unit_values = {key: item for key, item in dict.items(values)}
    else:
        unit_values = {}
    unit_values.setdefault(
        "run_registry_line",
        "run record " + _safe_str(run_id) + " read in one lookup")
    provenance = {
        "record": run_id,
        "record_state": record.get("record_state", "as retained"),
        "inside_unit": True,
    }
    unit_values["checkability_fields"] = provenance
    unit = make_headline_unit(unit_values)
    return {"built": True, "failure": None, "unit": unit}


def _stored_pair_present(record, field):
    """Whether a handed record carries a field among its stored
    pairs, a field standing present where a stored key carries
    its name in stored text, never through a hash or equality
    reading a handed key supplies, in the posture of the cured
    MOD-13 _base_get of row R18-033."""
    if not isinstance(record, dict):
        return False
    for key in dict.keys(record):
        if any(key_text is not None and str.__eq__(key_text, field)
               for key_text in _registry_key_texts(key)):
            return True
    return False


def _stored_identifier_form(value, _depth=0, _seen=None):
    """The stored form of one headline unit identifier, built
    from the contents it stores through the base readings of
    its form, never through a repr, equality, or hash reading
    the value itself supplies, in the form the MOD-14 sister
    act weekly_headline_count states for its keying: text by
    its stored characters, a boolean apart from every number,
    a plain number by the number it stores, a Decimal or a
    Fraction by its base string form, a buffer by its stored
    bytes, and a container part by part under this same
    reading, dicts by their stored pairs in order, lists and
    tuples in order, and sets and frozensets apart from each
    other and order insensitively. A part in no stated form
    stands keyed by its kind name alone, and a part standing
    deeper than the depth bound of 100, or standing again on
    its own walk path, stands keyed by a stated marker in
    that posture."""
    if isinstance(value, bool):
        return ("bool", value is True)
    if isinstance(value, str):
        return ("text", str.__str__(value))
    if isinstance(value, int):
        return ("int", int.__int__(value))
    if isinstance(value, float):
        return ("float", float.__float__(value))
    if isinstance(value, Decimal):
        return ("decimal", Decimal.__str__(value))
    if isinstance(value, Fraction):
        return ("fraction", Fraction.__str__(value))
    if isinstance(value, (bytes, bytearray, memoryview)):
        return ("bytes", bytes(value))
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > 100:
            return ("too deep",)
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            return ("cycle",)
        seen = seen | {id(value)}
        if isinstance(value, dict):
            return ("dict", tuple(
                (_stored_identifier_form(key, _depth + 1, seen),
                 _stored_identifier_form(item, _depth + 1, seen))
                for key, item in dict.items(value)))
        if isinstance(value, list):
            return ("list", tuple(
                _stored_identifier_form(item, _depth + 1, seen)
                for item in list.__iter__(value)))
        if isinstance(value, tuple):
            return ("tuple", tuple(
                _stored_identifier_form(item, _depth + 1, seen)
                for item in tuple.__iter__(value)))
        if isinstance(value, frozenset):
            return ("frozenset", frozenset(
                _stored_identifier_form(item, _depth + 1, seen)
                for item in frozenset.__iter__(value)))
        return ("set", frozenset(
            _stored_identifier_form(item, _depth + 1, seen)
            for item in set.__iter__(value)))
    if value is None:
        return ("none",)
    return ("kind", type(value).__name__)


def weekly_count(summary_records, week):
    """Compute the weekly headline reading load from the stored
    summary records alone: distinct headline unit identifiers
    whose witness records fall in the week, one unit counting
    once however many runs support it. The failures of the
    count stand stated in the split forms its sister act at
    MOD-14 states: a record with no week field, and a record
    of the week with no headline unit identifier field, fail
    apart, in the named form; neither is counted silently as
    zero. A record of another week stands passed over, its
    identifier field never read. A record of the week whose
    identifier field stands at None, or in a form the count
    cannot read as a list of identifiers, fails in the same
    named form. A bare string identifier field counts as the
    one identifier it states, never as its characters. The
    records argument itself stands in list form or the count
    stands refused in the same named list form its sister act
    at MOD-14 states. Each record stands read through the base
    dict readings, never through a get or contains reading the
    record itself supplies, and the identifier field stands
    read through the base iteration of its form, with
    distinctness judged on the stored text of each identifier,
    never through an iteration or equality reading a handed
    value supplies. A container identifier stands keyed on
    the stored form it carries, built through the base
    readings of its form, never on a repr reading the
    identifier itself supplies, so two distinct container
    identifiers sharing one supplied repr stand counted as
    the two units they are, and two container identifiers
    storing the same contents stand counted as one. An
    identifier standing in no headline unit
    identifier form stands refused in named form, as the weekly
    container of this module refuses it, so no count stands
    stated over unvalidated contents."""
    if summary_records is None:
        raise ValueError(
            "weekly_count stands refused: no summary_records "
            "stand supplied: a list of summary records stands "
            "required, and no weekly count stands certified "
            "without it")
    if week is None:
        raise ValueError(
            "weekly_count stands refused: no week stands "
            "supplied: a week stands required, and no weekly "
            "count stands certified without it")
    if not isinstance(summary_records, (list, tuple, set, frozenset)):
        raise ValueError(
            "weekly_count stands refused: the summary_records "
            "argument stands in no list form: a list of summary "
            "records stands required, and no weekly count stands "
            "certified without it")
    identifiers = []
    seen_texts = []
    for record in _base_iter(summary_records):
        if not isinstance(record, dict) or not _stored_pair_present(
                record, "week"):
            raise ValueError(
                "summary record carries no week field, so its "
                "weekly headline count cannot stand read")
        if not _week_stands_equal(
                _registry_stored_value(record, "week"), week):
            continue
        if not _stored_pair_present(
                record, "headline_unit_identifiers"):
            raise ValueError(
                "summary record for the week carries no "
                "headline_unit_identifiers field, and no weekly "
                "count stands certified without it")
        field = _registry_stored_value(
            record, "headline_unit_identifiers")
        if field is None:
            raise ValueError(
                "summary record for the week carries a "
                "headline_unit_identifiers field standing at "
                "no value, and no weekly count stands certified "
                "without it")
        if isinstance(field, str):
            field = (field,)
        elif not isinstance(field, (list, tuple, set, frozenset)):
            raise ValueError(
                "summary record for the week carries a "
                "headline_unit_identifiers field the count "
                "cannot read: " + type(field).__name__
                + ", and no weekly count stands certified "
                "without it")
        for identifier in _base_iter(field):
            if isinstance(identifier, (list, tuple, set, frozenset,
                                       dict)):
                key = ("container", _stored_identifier_form(identifier))
            elif _unit_identifier_stands(identifier):
                key = ("text", str.__str__(identifier))
            else:
                try:
                    rendered = _form_repr(identifier)
                except (KeyboardInterrupt, SystemExit):
                    rendered = type(identifier).__name__
                raise ValueError(
                    "summary record for the week carries an "
                    "identifier standing in no unit identifier "
                    "form, and no count stands stated over "
                    "unvalidated contents: " + rendered)
            if key not in seen_texts:
                seen_texts.append(key)
                identifiers.append(identifier)
    return len(identifiers)


def _week_plain_number(value):
    """The plain number a week value stores, built through
    base class operations, or None where the value stands in
    no plain number form: an integer week as a plain int and
    a float week as a plain float, so no equality reading a
    handed number supplies decides its own judgement."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return int.__new__(int, int.__int__(value))
    if isinstance(value, float):
        return float.__new__(float, float.__float__(value))
    return None


def _week_value_equal(stored, handed, _seen=None):
    """Judge two week values equal kind first at every level:
    two text values by the base text equality of their stored
    characters, a boolean only against a boolean, a Decimal
    only against a Decimal and a Fraction only against a
    Fraction, each by its base class equality on plain copies,
    two plain number values by the plain numbers they store,
    built through base class operations so no handed equality
    reading decides, and container values part by part under
    this same reading, lists and tuples in order, sets and
    frozensets order insensitively, and dicts by matched keys
    and their values. Any other pair stands equal only where
    both stand in the same kind, judged by a guarded equality
    that a raising reading answers as not equal."""
    if stored is None or handed is None:
        return stored is None and handed is None
    if isinstance(stored, str) or isinstance(handed, str):
        return (isinstance(stored, str) and isinstance(handed, str)
                and str.__eq__(stored, handed) is True)
    if isinstance(stored, bool) or isinstance(handed, bool):
        return (isinstance(stored, bool) and isinstance(handed, bool)
                and stored is handed)
    if isinstance(stored, Decimal) or isinstance(handed, Decimal):
        return (isinstance(stored, Decimal)
                and isinstance(handed, Decimal)
                and Decimal.__eq__(
                    Decimal.__new__(Decimal, stored),
                    Decimal.__new__(Decimal, handed)) is True)
    if isinstance(stored, Fraction) or isinstance(handed, Fraction):
        return (isinstance(stored, Fraction)
                and isinstance(handed, Fraction)
                and Fraction.__eq__(
                    Fraction.__new__(Fraction, stored),
                    Fraction.__new__(Fraction, handed)) is True)
    stored_number = _week_plain_number(stored)
    handed_number = _week_plain_number(handed)
    if stored_number is not None or handed_number is not None:
        return (stored_number is not None
                and handed_number is not None
                and stored_number == handed_number)
    if isinstance(stored, (bytes, bytearray, memoryview)) or isinstance(
            handed, (bytes, bytearray, memoryview)):
        return (isinstance(stored, (bytes, bytearray, memoryview))
                and isinstance(handed, (bytes, bytearray, memoryview))
                and bytes.__eq__(bytes(stored), bytes(handed)) is True)
    if isinstance(stored, dict) or isinstance(handed, dict):
        if not (isinstance(stored, dict) and isinstance(handed, dict)):
            return False
        seen = _seen if _seen is not None else set()
        pair = (id(stored), id(handed))
        if pair in seen:
            return True
        seen = seen | {pair}
        if dict.__len__(stored) != dict.__len__(handed):
            return False
        handed_items = list(dict.items(handed))
        used = [False] * len(handed_items)
        for stored_key, stored_item in dict.items(stored):
            matched = False
            for index in range(len(handed_items)):
                if used[index]:
                    continue
                handed_key, handed_item = handed_items[index]
                if _week_value_equal(
                        stored_key, handed_key, seen) and (
                        _week_value_equal(
                            stored_item, handed_item, seen)):
                    used[index] = True
                    matched = True
                    break
            if not matched:
                return False
        return True
    if isinstance(stored, list) or isinstance(handed, list):
        if not (isinstance(stored, list) and isinstance(handed, list)):
            return False
        seen = _seen if _seen is not None else set()
        pair = (id(stored), id(handed))
        if pair in seen:
            return True
        seen = seen | {pair}
        stored_parts = list(list.__iter__(stored))
        handed_parts = list(list.__iter__(handed))
        return len(stored_parts) == len(handed_parts) and all(
            _week_value_equal(part, other, seen)
            for part, other in zip(stored_parts, handed_parts))
    if isinstance(stored, tuple) or isinstance(handed, tuple):
        if not (isinstance(stored, tuple)
                and isinstance(handed, tuple)):
            return False
        seen = _seen if _seen is not None else set()
        pair = (id(stored), id(handed))
        if pair in seen:
            return True
        seen = seen | {pair}
        stored_parts = list(tuple.__iter__(stored))
        handed_parts = list(tuple.__iter__(handed))
        return len(stored_parts) == len(handed_parts) and all(
            _week_value_equal(part, other, seen)
            for part, other in zip(stored_parts, handed_parts))
    if isinstance(stored, (set, frozenset)) or isinstance(
            handed, (set, frozenset)):
        if isinstance(stored, set) != isinstance(handed, set):
            return False
        if isinstance(stored, frozenset) != isinstance(
                handed, frozenset):
            return False
        seen = _seen if _seen is not None else set()
        pair = (id(stored), id(handed))
        if pair in seen:
            return True
        seen = seen | {pair}
        if isinstance(stored, frozenset):
            stored_parts = list(frozenset.__iter__(stored))
            handed_parts = list(frozenset.__iter__(handed))
        else:
            stored_parts = list(set.__iter__(stored))
            handed_parts = list(set.__iter__(handed))
        if len(stored_parts) != len(handed_parts):
            return False
        remaining = list(handed_parts)
        for part in stored_parts:
            matched = None
            for index, other in enumerate(remaining):
                if _week_value_equal(part, other, seen):
                    matched = index
                    break
            if matched is None:
                return False
            remaining.pop(matched)
        return True
    if type(stored) is not type(handed):
        return False
    try:
        return bool(stored == handed)
    except Exception:
        return False


def _week_stands_equal(stored_week, handed_week):
    """Judge two week values equal on their stored text alone
    where both stand in text form, through the base text
    equality, never through an equality reading a handed or
    stored value supplies. Values in other forms stand judged
    kind first at every level under _week_value_equal: a
    boolean week only against a boolean week, a plain number
    week by the plain number it stores, and a container week
    part by part under the same kind first reading, so a
    boolean, a Decimal, or a Fraction standing inside a
    container week never stands equal to a plain number."""
    return _week_value_equal(stored_week, handed_week)


_UNIT_IDENTIFIER_PATTERN = re.compile(r"u[0-9]+")


def _unit_identifier_stands(item):
    """Return True only where an item stands as one headline unit
    identifier in the standing form the weekly pins use: the
    letter u followed by one or more plain digits, and nothing
    else."""
    return isinstance(item, str) and \
        _UNIT_IDENTIFIER_PATTERN.fullmatch(item) is not None


def _stored_unit_list(value):
    """The stored parts of a handed unit container, read through
    the base iteration of its form, never through an iteration
    the value itself supplies. A value in no container form
    stores no units."""
    if isinstance(value, (list, tuple, set, frozenset)):
        return list(_base_iter(value))
    return []


def make_weekly_container(week, units):
    """Build the weekly container for one week in arrival order.
    At most 25 whole headline units stand in the container under
    decision D-12. A unit beyond the cap stands held, reported as
    held in the container record of its own week. Each held item
    stands validated against the standing unit identifier form
    before any count stands taken, and an item that does not
    stand in that form stands refused in named form, so no count
    stands stated over unvalidated contents. The population
    stands judged as a set of identities: a unit identifier
    handed more than once stands in the container once, in its
    first arrival position, judged on the stored text of the
    identifier, so a repeat consumes no place inside the cap and
    stands nowhere among the held units, in the same identity
    reading the weekly count states."""
    ordered = _stored_unit_list(units)
    for item in ordered:
        if not _unit_identifier_stands(item):
            try:
                rendered = _form_repr(item)
            except (KeyboardInterrupt, SystemExit):
                rendered = type(item).__name__
            raise ValueError(
                "weekly container stands refused in named form: "
                "a held item stands in no unit identifier form, "
                "and no count stands taken over unvalidated "
                "contents: " + rendered)
    distinct = []
    seen_texts = []
    for item in ordered:
        text = str.__str__(item)
        if text not in seen_texts:
            seen_texts.append(text)
            distinct.append(item)
    inside = distinct[:WEEKLY_CAP]
    held = distinct[WEEKLY_CAP:]
    outside_cells = sum(
        int(unit.get("outside_unit_cells") or 0)
        for unit in inside if isinstance(unit, dict))
    load = {"H": len(inside), "U": outside_cells}
    return {
        "week": week,
        "cap": WEEKLY_CAP,
        "cap_form": "estimated planning figure under D-12: at most 25 headline results per week for one operator, estimated",
        "weekly_load": load,
        "load_statement": (
            "the priced reading load stands exceeded"
            if load["H"] + load["U"] > WEEKLY_CAP
            else "the priced reading load stands within the estimated figure"),
        "headline_units": inside,
        "held_units": held,
        "held_count": len(held),
        "held_reported_as_held": bool(held),
        "count": len(inside),
    }


def next_weekly_container(week, previous_container, new_units):
    """Build the next weekly container: units held from the
    previous container stand released into it first, in arrival
    order, ahead of the new units of the week."""
    released = _stored_unit_list(
        dict.get(previous_container, "held_units")
        if isinstance(previous_container, dict) else None)
    return make_weekly_container(
        week, released + _stored_unit_list(new_units))


def claim_enters_family(family_record, claim, results_seen):
    """Return True only where a claim may enter a family: the
    family stands fixed before runs, and no claim enters the
    family after results are seen."""
    if results_seen:
        return False
    if not isinstance(family_record, dict):
        return False
    claim_text = _registry_stored_text(claim)
    if claim_text is None:
        return False
    return any(
        stored_text is not None
        and str.__eq__(stored_text, claim_text)
        for stored_text in (
            _registry_stored_text(stored)
            for stored in _stored_unit_list(
                dict.get(family_record, "headline_claims"))))


_VISUAL_PRESENTATIONS = ("position", "extent", "colour", "layout")


def validate_readout(readout):
    """Return True only under the readout equivalence duty of
    Amendment TG4-56: every quantity presented by position,
    extent, colour, or layout also stands in the same readout as
    a recorded number, and any class rule a quantity rests on
    stands stated in words in the same unit. A readout presenting
    a quantity only in a visual or positional form is not
    published, and this function returns False for it."""
    if not isinstance(readout, dict):
        return False
    quantities = dict.get(readout, "quantities")
    if not isinstance(quantities, (list, tuple)) or (list.__len__(quantities) if isinstance(quantities, list) else tuple.__len__(quantities)) == 0:
        return False
    for quantity in _base_iter(quantities):
        if not isinstance(quantity, dict):
            return False
        name = dict.get(quantity, "name")
        if not isinstance(name, str) \
                or len(str.strip(str.__str__(name))) < 2 \
                or _plain_word_count(name) < 1:
            return False
        number = dict.get(quantity, "recorded_number")
        if isinstance(number, bool) or not isinstance(number, (int, float)):
            return False
        if dict.get(quantity, "class_based"):
            rule = dict.get(quantity, "class_rule")
            if not isinstance(rule, str) \
                    or not str.strip(str.__str__(rule)):
                return False
            if _plain_word_count(rule) < 3:
                return False
    return True


def validate_disclosure_form(form):
    """Return True only under the disclosure form identification
    duty of Amendment TG4-64: every entry of a disclosure table,
    triangle, or period form states its reported quantity with
    its row identifier and its column or period identifier
    attached to the quantity itself, in the fixed order row,
    column or period, quantity, a form that survives removal of
    the layout. A form whose quantities are identified only by
    their position on the page is not published, and this
    function returns False for it."""
    if not isinstance(form, dict):
        return False
    entries = dict.get(form, "entries")
    if not isinstance(entries, (list, tuple)) or (list.__len__(entries) if isinstance(entries, list) else tuple.__len__(entries)) == 0:
        return False
    for entry in _base_iter(entries):
        if not isinstance(entry, dict):
            return False
        keys = tuple(dict.keys(entry))
        if keys not in (("row", "column", "quantity"),
                        ("row", "period", "quantity")):
            return False
        for identifier in (dict.__getitem__(entry, "row"), dict.__getitem__(entry, keys[1])):
            if identifier is None or (isinstance(identifier, str)
                                      and not str.strip(
                                          str.__str__(identifier))):
                return False
        quantity = dict.__getitem__(entry, "quantity")
        if isinstance(quantity, bool) or not isinstance(
                quantity, (int, float)):
            return False
    return True


# The named carriage keys of a made family record, in the
# MOD-12 made record form (Step 16 fix wave 2, row F2-01,
# ruling T16-23). The seal and edit keys of MOD-12 stand
# beside them only in the form the product own seal and edit
# acts write them, as _legitimate_wider_keys states (Step 16
# fix wave 3, row F3-01, ruling T16-39).
_FAMILY_CARRIAGE_KEYS = (
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

_FAMILY_SEAL_KEYS = (
    "seal",
    "seal_version",
    "seal_hash",
    "sweep_manifest",
)

_FAMILY_EDIT_KEYS = (
    "runs_under",
    "edited_after_seal",
    "identifier_changed",
    "runs_start_again",
)


_SEAL_NO_HASH_STANDING = (
    "no hash value stands on the record; "
    "no hash stands computed by this seal")

_SEAL_RECORDED_HASH_STANDING = (
    "hash value as recorded on the record, "
    "stated as the hash")

_EDITED_IDENTIFIER_SUFFIX = "-edited-1"


def _seal_form_stands(family_record):
    """Whether the sealed standing of one family record stands
    in the form the product own seal act writes it (Step 16
    fix wave 4, row F4-01, ruling T16-49), in the same
    settlement MOD-01 and MOD-12 state: the record stands
    sealed, the seal stands as a record value carrying the
    version, hash, and hash standing keys alone, the seal
    version and the seal hash stand equal to the version and
    the hash the seal itself carries, the family manifest hash
    stands equal to that hash, the hash standing stands in the
    form the seal act writes for the hash it carries, the seal
    version stands as the family version the record carries or
    as the seal act default where no version value stands, and
    the sweep manifest stands as the manifest the sweep act
    produces for the record as it stands, its family
    identifier, its family version, and its sealed family
    record hash, the first hash value standing among the
    family manifest hash, the seal hash, and the seal hash
    itself. A sealed standing in any other form stands in no
    form the seal act writes."""
    if _registry_stored_value(family_record, "sealed") is not True:
        return False
    seal = _registry_stored_value(family_record, "seal")
    if not isinstance(seal, dict):
        return False
    seal_fields = set()
    for key, _item in list(dict.items(seal)):
        text = _registry_stored_text(key)
        if text is not None:
            seal_fields.add(text)
    if seal_fields != {"version", "hash", "hash_standing"}:
        return False
    version = _registry_stored_value(seal, "version")
    hash_value = _registry_stored_value(seal, "hash")
    hash_standing = _registry_stored_value(seal, "hash_standing")
    if not mod01._base_value_equals(
            _registry_stored_value(family_record, "seal_version"),
            version):
        return False
    if not mod01._base_value_equals(
            _registry_stored_value(family_record, "seal_hash"),
            hash_value):
        return False
    if not mod01._base_value_equals(
            _registry_stored_value(
                family_record, "family_manifest_hash"),
            hash_value):
        return False
    standing_text = _registry_stored_text(hash_standing)
    if hash_value is None:
        if standing_text is None or not str.__eq__(
                standing_text, _SEAL_NO_HASH_STANDING):
            return False
    elif mod01._stored_value_present(hash_value):
        if standing_text is None or not str.__eq__(
                standing_text, _SEAL_RECORDED_HASH_STANDING):
            return False
    else:
        return False
    family_version = _registry_stored_value(
        family_record, "family_version")
    expected_version = (
        family_version if mod01._stored_value_present(family_version)
        else "version 1")
    if not mod01._base_value_equals(version, expected_version):
        return False
    manifest = _registry_stored_value(family_record, "sweep_manifest")
    if not isinstance(manifest, dict):
        return False
    manifest_fields = set()
    for key, _item in list(dict.items(manifest)):
        text = _registry_stored_text(key)
        if text is not None:
            manifest_fields.add(text)
    if manifest_fields != {
            "family_identifier", "family_version",
            "sealed_family_record_hash"}:
        return False
    if _stored_pair_present(family_record, "family_identifier"):
        identifier_value = _registry_stored_value(
            family_record, "family_identifier")
    else:
        identifier_value = _registry_stored_value(
            family_record, "family_id")
    sealed_hash = None
    for candidate in (
            _registry_stored_value(
                family_record, "family_manifest_hash"),
            _registry_stored_value(family_record, "seal_hash"),
            hash_value):
        if mod01._stored_value_present(candidate):
            sealed_hash = candidate
            break
    expected_manifest = {
        "family_identifier": identifier_value,
        "family_version": family_version,
        "sealed_family_record_hash": sealed_hash,
    }
    for field in ("family_identifier", "family_version",
                  "sealed_family_record_hash"):
        if not mod01._base_value_equals(
                _registry_stored_value(manifest, field),
                expected_manifest[field]):
            return False
    return True


def _legitimate_wider_keys(family_record):
    """The seal and edit keys of one family record that stand
    in the form the product own seal and edit acts write them
    (Step 16 fix wave 3, row F3-01, ruling T16-39, as settled
    at Step 16 fix wave 4, row F4-01, ruling T16-49), in the
    same settlement MOD-01 and MOD-12 state: the seal keys
    together on a record whose sealed standing stands in the
    form the seal act writes it, as _seal_form_stands states;
    the edit keys together with each marker standing as True,
    the runs under value standing as the family identifier
    the record carries, that identifier standing in the edited
    form the edit act writes, carrying the edited suffix that
    act appends, and the record standing unsealed as that act
    leaves it, or standing sealed in the seal act form where
    a later seal carried the edit keys through; or the runs
    under key alone carrying that identifier with no edit
    marker beside it."""
    if not isinstance(family_record, dict):
        return set()
    try:
        present = set()
        for key, _item in list(dict.items(family_record)):
            text = _registry_stored_text(key)
            if text is not None:
                present.add(text)
    except Exception:
        return set()
    legitimate = set()
    seal_form = _seal_form_stands(family_record)
    if all(key in present for key in _FAMILY_SEAL_KEYS):
        if seal_form:
            legitimate.update(_FAMILY_SEAL_KEYS)
    identifier_text = _registry_stored_text(
        _registry_stored_value(family_record, "family_id"))
    if identifier_text is None:
        identifier_text = _registry_stored_text(
            _registry_stored_value(family_record, "family_identifier"))
    runs_text = _registry_stored_text(
        _registry_stored_value(family_record, "runs_under"))
    runs_matches = (
        runs_text is not None and identifier_text is not None
        and str.__eq__(runs_text, identifier_text))
    edited_form = (
        identifier_text is not None
        and str.endswith(identifier_text, _EDITED_IDENTIFIER_SUFFIX)
        and (_registry_stored_value(family_record, "sealed") is False
             or seal_form))
    if all(key in present for key in _FAMILY_EDIT_KEYS):
        if _registry_stored_value(
                family_record, "edited_after_seal") is True and (
                _registry_stored_value(
                    family_record, "identifier_changed") is True) and (
                _registry_stored_value(
                    family_record, "runs_start_again") is True) and (
                runs_matches) and edited_form:
            legitimate.update(_FAMILY_EDIT_KEYS)
    elif "runs_under" in present and not any(
            key in present for key in _FAMILY_EDIT_KEYS[1:]):
        if runs_matches:
            legitimate.add("runs_under")
    return legitimate


def _unnamed_family_fields(family_record):
    """The stored keys of one family record standing outside
    the Form 1 fields, the completeness brief names, and the
    named carriage keys, each named by the text it stores.
    The keys stand read through base dict operations on the
    stored pairs, never through a reading the handed record
    supplies."""
    allowed = set(mod01.form_fields("1"))
    allowed.update(mod01.COMPLETENESS_FIELDS)
    allowed.update(_FAMILY_CARRIAGE_KEYS)
    allowed.update(_legitimate_wider_keys(family_record))
    unnamed = []
    for key, _item in list(dict.items(family_record)):
        text = _registry_stored_text(key)
        if text is None:
            try:
                text = str(key)
            except Exception:
                text = object.__repr__(key)
            unnamed.append(text)
        elif text not in allowed:
            unnamed.append(text)
    return unnamed


def validate_family_record(family_record):
    """Return whether a family record passes MOD-01 validation
    for Form 1 and supports a reportable run under its
    completeness bar. A record carrying a field standing
    outside the Form 1 fields, the completeness brief names,
    and the named carriage keys stands refused here, in place
    of passing on the inner judgement alone (Step 16 fix wave
    2, row F2-01, ruling T16-23). A record sealed by the product
    own seal act or edited by the product own edit acts keeps
    its standing here on the keys those acts write, in the form
    they write them (Step 16 fix wave 3, row F3-01, ruling
    T16-39)."""
    if not isinstance(family_record, dict):
        return False
    if _unnamed_family_fields(family_record):
        return False
    if not mod01._validate_record_bool("1", family_record):
        return False
    return mod01.family_supports_reportable_run(family_record)


__all__ = [
    "HEADLINE_UNIT_FIELDS",
    "REGISTRY_FIELDS",
    "RETIREMENT_CHECKS",
    "WEEKLY_CAP",
    "AXES",
    "F01_UNIT_MARK",
    "retirement_verdicts",
    "retirement_tally",
    "validate_publication_record",
    "unit_is_publishable",
    "judge_registry_entry",
    "validate_registry_entry",
    "make_headline_unit",
    "validate_headline_unit",
    "quote_headline_unit",
    "first_sentence",
    "validate_working_range_claim",
    "moved_reading",
    "validate_bounding_headline",
    "validate_envelope_claim",
    "honest_loss_rate_h1",
    "top_up_applies",
    "point_standing",
    "classify_run_outcome",
    "transition_figure",
    "location_for_endpoint",
    "record_first_observed",
    "validate_observation_time",
    "region_shift_steps",
    "transition_wording",
    "validate_transition_report",
    "validate_transition_unit",
    "reporter_inputs_for_family",
    "share_report_stands",
    "build_headline_unit_from_run",
    "weekly_count",
    "make_weekly_container",
    "next_weekly_container",
    "claim_enters_family",
    "validate_family_record",
    "validate_readout",
    "validate_disclosure_form",
]

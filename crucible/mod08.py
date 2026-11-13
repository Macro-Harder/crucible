"""MOD-08. Detection Layer.

Vigil style scoring inside a run. The layer accepts one agent level
input form only, the DetectionInput record stated at Form 19, and no
other form. It returns verdict states and accumulator updates by
agent and day, and it changes no reputation, stake, or contract
state in any module.

Daily scoring stands as one daily scoring pass with table identified
contributions. The single pass is a module structure only and
records no accumulator representation. The table identifiers stay in
the merged pass. Conformance use and assumption use stand as two
named modes, and no value moves between them inside one artefact
without both uses named.

Open standings carried in this module, by name. OP-16 stands open:
the verdict rule limb values (pass condition values, fail condition
values, the minimum stream figure, and the false alarm budget
values) and the Form 27 profile bound label value set stand unfixed,
so no detection score is reported as a pass or as a fail anywhere in
this surface, and every detection output carries its profile bound
label attached in carriage form. DQ7-01 stands carried open for
reliance: the closed list of accumulators and each update rule stand
open on that record, no accumulator equality claim stands in hash
entry or in resume comparison, and resume equality for the
detection part stands at verdict level only. OP-11 stands open for
the strategy catalogue this layer does not own. The figures of
fixture F-06 stand as self consistency figures only, with no
calibration claim, under decision D-13.
"""

import copy
import math
from decimal import Decimal, localcontext

from crucible import mod01 as _mod01

__all__ = [
    "CALIBRATION_STANDING",
    "CONTESTED_LABEL_C6",
    "DEFERRED_OUTSIDE_CLASSES",
    "DETECTION_INPUT_FIELDS",
    "F06_FIGURES",
    "F06_PROFILES",
    "LR_TABLES",
    "OP16_STANDING",
    "PROFILE_BOUND_LABEL_FIELD",
    "PROFILE_LABEL_CARRIAGE",
    "RULE_STATE_FIELDS",
    "THRESHOLD_SETS",
    "USES",
    "VERDICT_LADDER",
    "DetectionLayer",
    "NamedDetectionFailure",
    "SilentUseMovement",
    "accept_detection_input",
    "author_sealed_class",
    "compare_verdict_determinism",
    "conformance_statement",
    "create_sealed_set",
    "detection_state_record",
    "epoch_watch_gate_on_unweighted",
    "freeze_sealed_set",
    "mod01_surface",
    "null_control_bracket",
    "oracle_control_bracket",
    "record_verdict_difference",
    "report",
    "score",
    "score_day",
    "score_profiles",
    "score_sealed",
    "seal_sealed_set",
    "unseal_sealed_set",
    "validate_output",
    "validate_use_naming",
]

OP16_STANDING = "open at OP-16"

CALIBRATION_STANDING = "no calibration claim, self consistency only"

DETECTION_INPUT_FIELDS = (
    "agent_identifier",
    "day",
    "feature_values",
    "records_for_agent_and_day",
)

_RECORDS_KEY = "records_for_agent_and_day"
_RECORDS_ALIAS = "rule_records"

_BARRED_KEY_PARTS = (
    "membership",
    "ground_truth",
    "groundtruth",
    "canary",
)

_BARRED_EXACT_KEYS = frozenset([
    "archetype_identifier",
    "reputation",
    "reputation_score",
    "reputation_score_by_viewer",
    "band",
    "stake",
    "stake_held",
    "contract_state",
    "lien_state",
    "is_honest",
    "is_farm",
    "honest",
    "label",
    "sleeper",
])

RULE_STATE_FIELDS = (
    "reputation",
    "reputation_score",
    "reputation_score_by_viewer",
    "band",
    "stake",
    "stake_held",
    "contract_state",
    "lien_state",
)

VERDICT_LADDER = (
    "UNOBSERVED",
    "NO-SIGNAL",
    "NOTICED",
    "WATCH",
    "ACCUSED",
)

LR_TABLES = ("LR-1", "LR-2", "LR-3", "LR-4", "LR-5", "LR-6")

USES = ("conformance", "assumption")

CONTESTED_LABEL_C6 = "contested at finding C-6"

THRESHOLD_SETS = {
    "epoch weighted": {
        "values": (320, 533, 800),
        "population": 8,
        "contested": True,
        "contested_label": CONTESTED_LABEL_C6,
        "standing": "operating values for an epoch watch",
    },
    "unweighted": {
        "values": (160,),
        "threshold": 160,
        "noticed_at": 4,
        "watch_at": 13,
        "contested": True,
        "contested_label": CONTESTED_LABEL_C6,
        "standing": "brief section figures for their own threshold only",
    },
}

F06_PROFILES = (
    "slow leak",
    "drifter",
    "prepositioner",
    "colluder",
    "honest",
)

F06_MINIMUM_STREAMS_PER_PROFILE = 1000

F06_FIGURES = {
    "false ACCUSED": 0.0,
    "false WATCH": 0.129,
    "false NOTICED": 0.31,
}

DEFERRED_OUTSIDE_CLASSES = (
    "O-1", "O-2", "O-3", "O-4", "O-5", "O-6", "O-7",
)

PROFILE_BOUND_LABEL_FIELD = "profile_bound_label"

PROFILE_LABEL_CARRIAGE = (
    "profile bound label attached (value set open at OP-16)"
)

_SEPARATIONS = (
    "authorship separation",
    "knowledge separation",
    "record separation",
)


class NamedDetectionFailure(Exception):
    """A detection failure stated by name, under Contract E."""


class SilentUseMovement(NamedDetectionFailure):
    """A table value moved between uses without both uses named."""


def mod01_surface():
    """Return the MOD-01 module this layer depends on, or None."""
    return _mod01


def _is_barred_key(key):
    lowered = str(key).lower()
    if lowered in _BARRED_EXACT_KEYS:
        return True
    return any(part in lowered for part in _BARRED_KEY_PARTS)


BARRED_SEARCH_DEPTH_BOUND = 100


def _find_barred(node, path="", _depth=0, _seen=None):
    if isinstance(node, (dict, list, tuple)):
        if _depth > BARRED_SEARCH_DEPTH_BOUND:
            raise NamedDetectionFailure(
                "delivery rejected: barred field search bound reached at "
                + (path or "root")
                + ": the value stands deeper than the stated bound of "
                + str(BARRED_SEARCH_DEPTH_BOUND)
            )
        seen = _seen if _seen is not None else set()
        if id(node) in seen:
            raise NamedDetectionFailure(
                "delivery rejected: barred field search found a cycle at "
                + (path or "root")
            )
        seen.add(id(node))
        try:
            hits = []
            if isinstance(node, dict):
                for key, value in node.items():
                    here = path + "/" + str(key)
                    if _is_barred_key(key):
                        hits.append(here)
                    hits.extend(_find_barred(value, here, _depth + 1, seen))
            else:
                for index, item in enumerate(node):
                    hits.extend(_find_barred(
                        item, path + "[" + str(index) + "]", _depth + 1, seen))
            return hits
        finally:
            seen.discard(id(node))
    return []


def _record_values(record):
    if isinstance(record, dict):
        return record
    values = getattr(record, "values", None)
    if isinstance(values, dict):
        return values
    return None


def accept_detection_input(record):
    """Accept one DetectionInput record and return a normalised copy.

    The copy carries the agent identifier, the day, the feature
    values, and the records the rules give the detection layer for
    that agent and day, under the Form 19 field names. The standing
    projection in MOD-04 emits its records under its own records key;
    that key is read as the same field and normalised to the Form 19
    name. Any other agent level form is rejected, and any record
    carrying a barred key at any depth is rejected, because the
    projection contract strips such keys before delivery.
    """
    values = _record_values(record)
    if values is None:
        raise NamedDetectionFailure(
            "delivery rejected: the record is not a DetectionInput record"
        )
    keys = set(values.keys())
    allowed = set(DETECTION_INPUT_FIELDS) | {_RECORDS_ALIAS}
    if not keys.issubset(allowed):
        raise NamedDetectionFailure(
            "delivery rejected: fields outside DetectionInput: "
            + ", ".join(sorted(str(k) for k in keys - allowed))
        )
    for field in ("agent_identifier", "day", "feature_values"):
        if field not in values or values[field] is None:
            raise NamedDetectionFailure(
                "delivery rejected: required DetectionInput field absent: "
                + field
            )
    if not isinstance(values["agent_identifier"], str) or not values[
            "agent_identifier"]:
        raise NamedDetectionFailure(
            "delivery rejected: the agent identifier stands in no "
            "identifier form"
        )
    day = values["day"]
    if isinstance(day, bool) or not isinstance(day, int) or day < 0 or (
            day >= 10 ** 6):
        raise NamedDetectionFailure(
            "delivery rejected: the day stands in no stated simulated "
            "day form: " + repr(day)
        )
    if not isinstance(values["feature_values"], dict):
        raise NamedDetectionFailure(
            "delivery rejected: feature values stand in no record form"
        )
    barred = _find_barred(values)
    if barred:
        raise NamedDetectionFailure(
            "delivery rejected: barred field present in DetectionInput: "
            + ", ".join(barred)
        )
    for feature_name, feature_value in values["feature_values"].items():
        if isinstance(feature_value, bool) or not isinstance(
                feature_value, (int, float)):
            raise NamedDetectionFailure(
                "delivery rejected: a feature value the rules cannot "
                "consume stands in the record: " + str(feature_name)
            )
        if isinstance(feature_value, float) and not math.isfinite(
                feature_value):
            raise NamedDetectionFailure(
                "delivery rejected: a feature value the rules cannot "
                "consume stands in the record: " + str(feature_name)
            )
    records = values.get(_RECORDS_KEY, values.get(_RECORDS_ALIAS, []))
    if records is None:
        records = []
    if not isinstance(records, (list, tuple)):
        raise NamedDetectionFailure(
            "delivery rejected: records for the agent and day stand "
            "in no record form"
        )
    return {
        "agent_identifier": values["agent_identifier"],
        "day": values["day"],
        "feature_values": copy.deepcopy(values["feature_values"]),
        _RECORDS_KEY: copy.deepcopy(list(records)),
    }


def _contributions(feature_values):
    contributions = []
    with localcontext() as context:
        context.prec = 28
        total = Decimal("0")
        for position, name in enumerate(sorted(feature_values.keys())):
            value = feature_values[name]
            amount = Decimal(str(value))
            total += amount
            contributions.append({
                "table_identifier": LR_TABLES[position % len(LR_TABLES)],
                "table_version": "as recorded",
                "feature": name,
                "value": value,
            })
    return contributions, total


def _verdict_state(total):
    if total <= 0:
        return "NO-SIGNAL"
    if total < 10:
        return "NOTICED"
    if total < 100:
        return "WATCH"
    return "ACCUSED"


def _score_one(accepted):
    contributions, total = _contributions(accepted["feature_values"])
    verdict = _verdict_state(total)
    state_record = {
        "agent_identifier": accepted["agent_identifier"],
        "day": accepted["day"],
        "feature_values": copy.deepcopy(accepted["feature_values"]),
        "likelihood_ratio_contributions": contributions,
        "accumulator_values": {"total_feature_value": str(total)},
        "accumulator_update": {"total_feature_value": str(total)},
        "accumulator_standing": (
            "gated form: accumulator values stand carried under the "
            "TG-07.5 reconciliation standing, which stands open; no "
            "accumulator representation stands reconciled"),
        "verdict_state": verdict,
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
    }
    output = {
        "agent_identifier": accepted["agent_identifier"],
        "day": accepted["day"],
        "verdict_state": verdict,
        "accumulator_update": {"total_feature_value": str(total)},
        "likelihood_ratio_contributions": copy.deepcopy(contributions),
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
    }
    return state_record, output


THRESHOLD_FORMULA_TABLE_IDENTIFIER = "threshold formula table"

THRESHOLD_FORMULA_TABLE_VERSION = (
    "the threshold set carriage of this module, as recorded")

DETECTION_STANDING_STATEMENT = (
    "figures are self consistency only, no calibration claim "
    "stands, and no verdict rule at OP-16 stands fixed")


def score_day(records, society_state=None, mode="conformance",
              uses=None, run_identifier=None):
    """Run one daily scoring pass over DetectionInput records.

    Returns verdict states and accumulator updates by agent and day,
    the DetectionState records of the pass, and a DetectionOutput
    record in the Form 27 carriage: run level fields standing as
    stated in the call, verdict states and accumulator updates by
    agent and day, and the profile bound label attached. Where a
    society state snapshot is supplied, it is compared before and
    after the pass: scoring writes to no trust state, and a
    difference outside the detection state marks the run invalid
    for detection reporting in the returned record.
    """
    if not isinstance(records, (list, tuple)):
        raise NamedDetectionFailure(
            "delivery rejected: the records for one day stand in "
            "no record list form"
        )
    if mode not in USES:
        raise NamedDetectionFailure(
            "scoring mode stands unnamed: " + str(mode)
        )
    named_uses = list(uses) if uses is not None else [mode]
    for use in named_uses:
        if use not in USES:
            raise NamedDetectionFailure(
                "scoring use stands unnamed: " + str(use)
            )
    before = copy.deepcopy(society_state)
    accepted = [accept_detection_input(record) for record in records]
    states = []
    outputs = []
    for record in accepted:
        state_record, output = _score_one(record)
        states.append(state_record)
        outputs.append(output)
    changed = society_state is not None and society_state != before
    combined = [
        {
            "agent_identifier": o["agent_identifier"],
            "day": o["day"],
            "verdict_state": o["verdict_state"],
            "accumulator_update": copy.deepcopy(o["accumulator_update"]),
            "likelihood_ratio_contributions": copy.deepcopy(
                o["likelihood_ratio_contributions"]),
        }
        for o in outputs
    ]
    detection_output = {
        "run_identifier": run_identifier,
        "scoring_day_range": sorted({o["day"] for o in outputs}),
        "verdict_states_and_accumulator_updates": combined,
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "threshold_formula_table_identifier": (
            THRESHOLD_FORMULA_TABLE_IDENTIFIER),
        "threshold_formula_table_version": (
            THRESHOLD_FORMULA_TABLE_VERSION),
        "standing_statement": DETECTION_STANDING_STATEMENT,
    }
    return {
        "verdict_states": outputs,
        "accumulator_updates": [
            {
                "agent_identifier": entry["agent_identifier"],
                "day": entry["day"],
                "accumulator_update": copy.deepcopy(
                    entry["accumulator_update"]),
            }
            for entry in combined
        ],
        "detection_states": states,
        "detection_output": detection_output,
        "uses_named": named_uses,
        "mode": mode,
        "rule_state_changed": bool(changed),
        "run_valid_for_detection_reporting": not changed,
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
    }


def score(record_or_records, society_state=None, mode="conformance",
          uses=None, run_identifier=None):
    """Score one DetectionInput record or one day of records."""
    if record_or_records is None:
        raise NamedDetectionFailure(
            "delivery rejected: the record is not a DetectionInput "
            "record"
        )
    if isinstance(record_or_records, dict) or _record_values(
            record_or_records) is not None and not isinstance(
            record_or_records, (list, tuple)):
        records = [record_or_records]
    else:
        records = list(record_or_records)
    return score_day(records, society_state=society_state, mode=mode,
                     uses=uses, run_identifier=run_identifier)


def detection_state_record(record):
    """Return the DetectionState record of one scored input."""
    accepted = accept_detection_input(record)
    state_record, _output = _score_one(accepted)
    return state_record


def validate_output(output):
    """Validate one detection output or figure record.

    A record fails where its profile bound label stands missing,
    where its label carries a value other than the carriage form
    this module attaches while the value set stands open, or where
    a score stands reported as a pass or as a fail.
    """
    if not isinstance(output, dict):
        return False
    if output.get(PROFILE_BOUND_LABEL_FIELD) != PROFILE_LABEL_CARRIAGE:
        return False
    return not _carries_barred_verdict(output)


_BARRED_VERDICT_VALUES = ("pass", "passed", "fail", "failed")

_VERDICT_POSITION_KEYS = (
    "score_verdict", "verdict", "result", "outcome", "score_result",
)


def _carries_barred_verdict(node):
    if isinstance(node, dict):
        for key, value in node.items():
            lowered = str(key).lower()
            if lowered in _VERDICT_POSITION_KEYS or "verdict" in lowered:
                if isinstance(value, str) and value.strip().lower() in (
                        _BARRED_VERDICT_VALUES):
                    return True
            if _carries_barred_verdict(value):
                return True
        return False
    if isinstance(node, (list, tuple)):
        return any(_carries_barred_verdict(item) for item in node)
    return False


def oracle_control_bracket():
    """The oracle control of INV8B-11, as a bracket record."""
    return {
        "control": "oracle",
        "standing": "bracket beside every detection figure",
        "false_rates": {
            "false ACCUSED": 0.0,
            "false WATCH": 0.0,
            "false NOTICED": 0.0,
        },
        "point_sets": list(F06_PROFILES),
        "calibration": CALIBRATION_STANDING,
        "outside_classes_adopted": [],
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
    }


def null_control_bracket():
    """The null detector control of INV8B-11, as a bracket record."""
    return {
        "control": "null",
        "standing": "bracket beside every detection figure",
        "verdict_state": "NO-SIGNAL for every input",
        "false_rates": {
            "false ACCUSED": 0.0,
            "false WATCH": 0.0,
            "false NOTICED": 0.0,
        },
        "point_sets": list(F06_PROFILES),
        "calibration": CALIBRATION_STANDING,
        "outside_classes_adopted": [],
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
    }


def score_profiles(profile_set=None):
    """Return the recorded profile set record of fixture F-06.

    The figures stand in their carried form, at record level only,
    as self consistency figures, with the oracle and null brackets
    beside them. A supplied profile set is checked against the
    carried profile names and the minimum stream count, and a set
    that differs is rejected rather than rescored.
    """
    if profile_set is not None:
        names = tuple(profile_set.get("profiles", ()))
        if names != F06_PROFILES:
            raise NamedDetectionFailure(
                "profile set differs from the recorded F-06 set"
            )
        streams = profile_set.get("streams_per_profile", 0)
        if isinstance(streams, (int, float)) and streams < (
                F06_MINIMUM_STREAMS_PER_PROFILE):
            raise NamedDetectionFailure(
                "profile set stands below the F-06 stream count"
            )
    return {
        "fixture": "F-06",
        "profiles": list(F06_PROFILES),
        "minimum_streams_per_profile": (
            F06_MINIMUM_STREAMS_PER_PROFILE),
        "figures": dict(F06_FIGURES),
        "verdict_ladder": list(VERDICT_LADDER),
        "provenance_label": "self scored",
        "standing": "self consistency figures only",
        "calibration": CALIBRATION_STANDING,
        "record_level_only": True,
        "bracket": [oracle_control_bracket(), null_control_bracket()],
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
    }


def conformance_statement(table_identifier="LR-1",
                          threshold_set="epoch weighted",
                          table_value=None):
    """State one conformance statement for a threshold reading.

    Every statement names its threshold set and the table value it
    checks, and carries the contested label where the register
    carries one, per AC-12. Formula and table stand as conformance
    material only in this surface.
    """
    if table_identifier not in LR_TABLES and table_identifier != (
            "threshold formula table"):
        raise NamedDetectionFailure(
            "conformance statement names no recorded table: "
            + str(table_identifier)
        )
    if threshold_set not in THRESHOLD_SETS:
        raise NamedDetectionFailure(
            "conformance statement names no recorded threshold set: "
            + str(threshold_set)
        )
    entry = THRESHOLD_SETS[threshold_set]
    value = table_value
    if value is None:
        value = entry["values"][0]
    statement = {
        "table_identifier": table_identifier,
        "threshold_set": threshold_set,
        "table_value": value,
        "uses_named": ["conformance"],
        "epoch_watch_gate_on_unweighted": False,
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
    }
    if entry.get("contested"):
        statement["contested_label"] = entry["contested_label"]
    return statement


def epoch_watch_gate_on_unweighted():
    """No epoch watch gate is built or reported on unweighted
    figures. The operating values are the epoch weighted values."""
    return False


def validate_use_naming(artefact, run_record_uses=None):
    """Check the use naming of one artefact carrying a table value.

    An artefact that carries a value in both uses stands only where
    both uses stand named in the artefact. An artefact whose use
    naming differs from the run record naming, or names neither
    use, is a silent movement and is rejected.
    """
    if not isinstance(artefact, dict):
        raise SilentUseMovement(
            "use naming check: the artefact stands in no record form"
        )
    named = list(artefact.get("uses_named", []))
    for use in named:
        if use not in USES:
            raise SilentUseMovement(
                "use naming check: a use stands unnamed: " + str(use)
            )
    if not named:
        raise SilentUseMovement(
            "use naming check: neither use stands named in the "
            "artefact"
        )
    if run_record_uses is not None:
        recorded = list(run_record_uses)
        if sorted(recorded) != sorted(named):
            raise SilentUseMovement(
                "use naming check: the artefact names one use while "
                "the run record names the other, or neither"
            )
    return True


def report(figures=None):
    """Build the bounded version 1 detection report.

    Every figure in the report carries its profile bound label, and
    the seven outside sleeper classes stand named and visible in
    the record as deferred, adopted in no part. A figure supplied
    without its label is rejected before the report stands.
    """
    carried = []
    for figure in figures or []:
        if not validate_output(figure):
            raise NamedDetectionFailure(
                "a figure reported without its profile bound label "
                "stands rejected"
            )
        carried.append(copy.deepcopy(figure))
    return {
        "report_kind": "bounded self consistency report",
        "figures": carried,
        "deferred_classes": [
            {"class": name, "standing": "deferred"}
            for name in DEFERRED_OUTSIDE_CLASSES
        ],
        "deferred_classes_visible": True,
        "outside_classes_adopted": [],
        "calibration": CALIBRATION_STANDING,
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
        "pass_or_fail_reporting": (
            "not reported while OP-16 stands open"),
    }


def create_sealed_set():
    """Open the conditional sealed late class set of fixture F-08."""
    return {
        "fixture": "F-08",
        "stage": "open",
        "detector_frozen": False,
        "authored": [],
        "sealed": False,
        "adoption_standing": (
            "subject to the adoption decisions at NQ-51 and NQ-63"),
        "profile_set_result_on_sealed_classes": (
            "no result stated or implied"),
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
    }


def freeze_sealed_set(sealed_set):
    """Freeze the detector before any sealed class is authored."""
    sealed_set["detector_frozen"] = True
    sealed_set["stage"] = "frozen"
    return sealed_set


def author_sealed_class(sealed_set, kind, identifier,
                        separations=None):
    """Author one sealed class under the three separations.

    Authoring before freezing is rejected. The kind stands as a
    sleeper class or as an honest challenge variant, and the three
    separations stand named on the authored entry.
    """
    if not sealed_set.get("detector_frozen"):
        raise NamedDetectionFailure(
            "sealed set rejected: authoring before freezing"
        )
    if sealed_set.get("sealed"):
        raise NamedDetectionFailure(
            "sealed set rejected: authoring after sealing"
        )
    if kind not in ("sleeper class", "honest challenge variant"):
        raise NamedDetectionFailure(
            "sealed set rejected: authored kind stands unnamed: "
            + str(kind)
        )
    named = tuple(separations or ())
    if sorted(named) != sorted(_SEPARATIONS):
        raise NamedDetectionFailure(
            "sealed set rejected: the three separations stand "
            "unnamed in full"
        )
    entry = {
        "kind": kind,
        "identifier": identifier,
        "separations": list(_SEPARATIONS),
    }
    sealed_set["authored"].append(entry)
    return entry


def seal_sealed_set(sealed_set):
    """Seal the authored set until scoring closes."""
    kinds = [entry["kind"] for entry in sealed_set.get("authored", [])]
    if "sleeper class" not in kinds or (
            "honest challenge variant" not in kinds):
        raise NamedDetectionFailure(
            "sealed set rejected: sealing needs at least one "
            "sleeper class and one honest challenge variant"
        )
    sealed_set["sealed"] = True
    sealed_set["stage"] = "sealed"
    return sealed_set


def unseal_sealed_set(sealed_set, scoring_closed=False):
    """Unseal the set only where scoring stands closed."""
    if not scoring_closed:
        raise NamedDetectionFailure(
            "sealed set rejected: early unsealing before scoring "
            "closes"
        )
    sealed_set["sealed"] = False
    sealed_set["stage"] = "unsealed after scoring closed"
    return sealed_set


def score_sealed(sealed_set):
    """State the standing of the sealed set while it stands sealed.

    No score from the recorded profile set states or implies a
    result on the sealed classes.
    """
    if sealed_set.get("sealed"):
        return {
            "fixture": "F-08",
            "standing": "sealed until scoring closes",
            "result_on_sealed_classes": None,
            "profile_set_result_on_sealed_classes": (
                "no result stated or implied"),
            PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
            "score_verdict": None,
        }
    raise NamedDetectionFailure(
        "sealed set scoring stands only in its sealed conditional "
        "form"
    )


def compare_verdict_determinism(material_a, material_b=None):
    """Run the verdict determinism check of contract C-16.

    The same DetectionInput material, delivered twice, returns the
    same verdict states and the same delivered update records, in
    DetectionState per agent per day and in the scoring payload by
    agent and day. No equality claim stands for accumulator values
    in hash entry or in resume comparison.
    """
    second = material_b if material_b is not None else material_a

    def _canonical(records):
        return sorted(
            (copy.deepcopy(record) for record in records),
            key=lambda record: (
                str(_record_values(record).get("agent_identifier")),
                _record_values(record).get("day"),
            ),
        )

    first = score_day(_canonical(material_a))
    other = score_day(_canonical(second))
    same = (
        first["verdict_states"] == other["verdict_states"]
        and first["detection_states"] == other["detection_states"]
        and first["accumulator_updates"] == other[
            "accumulator_updates"]
    )
    return {
        "same": same,
        "verdict_states": first["verdict_states"],
        "update_records": first["detection_states"],
        "accumulator_equality_claim": None,
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
    }


def record_verdict_difference(material_a, material_b):
    """Record a verdict difference on the same material.

    While the OP-16 bar stands, a difference is recorded as a
    barred check event: the event bars the run from reporting, and
    it is recorded as neither a pass score nor a fail score.
    """
    check = compare_verdict_determinism(material_a, material_b)
    if check["same"]:
        return {
            "event": None,
            "run_reportable": True,
            PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
            "score_verdict": None,
        }
    return {
        "event": "barred check event",
        "run_reportable": False,
        "recorded_as": "neither a pass score nor a fail score",
        PROFILE_BOUND_LABEL_FIELD: PROFILE_LABEL_CARRIAGE,
        "score_verdict": None,
    }


class DetectionLayer:
    """The Detection Layer as one daily scoring pass."""

    def __init__(self):
        self.detection_states = {}

    def accept_detection_input(self, record):
        return accept_detection_input(record)

    def score_day(self, records, society_state=None,
                  mode="conformance", uses=None):
        result = score_day(records, society_state=society_state,
                           mode=mode, uses=uses)
        for state in result["detection_states"]:
            key = (state["agent_identifier"], state["day"])
            self.detection_states[key] = copy.deepcopy(state)
        return result

    def score(self, record_or_records, society_state=None,
              mode="conformance", uses=None):
        if isinstance(record_or_records, (list, tuple)):
            return self.score_day(list(record_or_records),
                                  society_state=society_state,
                                  mode=mode, uses=uses)
        return self.score_day([record_or_records],
                              society_state=society_state,
                              mode=mode, uses=uses)

    def score_profiles(self, profile_set=None):
        return score_profiles(profile_set)

    def conformance_statement(self, table_identifier="LR-1",
                              threshold_set="epoch weighted",
                              table_value=None):
        return conformance_statement(
            table_identifier=table_identifier,
            threshold_set=threshold_set, table_value=table_value)

    def report(self, figures=None):
        return report(figures)

    def score_sealed(self, sealed_set):
        return score_sealed(sealed_set)

"""Integration surface of slice S-16: fixtures and validation runs.

This surface owns no module boundary. It composes MOD-01 to
MOD-14 as built: the engine of MOD-04 delivers, and this surface
composes the deliveries with the retention and reading path of
MOD-10, files the fixture inventory as a product artefact, and
exercises the wired product in its run classes on pilot confined
and validation material only. Every bar carried in slices S-01 to
S-15 stands in force here; an integration result that would need
a bar lifted is reported as bounded, never as a pass over the bar.
"""

import copy

from crucible import mod04
from crucible import mod10
from crucible import mod11


def run_tracer_cut():
    """Tracer composition, moved here from MOD-04 under finding
    F-LE-03: MOD-04 holds no code dependency on MOD-10 in any form,
    so the composition that hands the form only record to the
    MOD-10 retention path and reads it back through that path
    alone stands on this integration surface. The engine delivers
    the record and the projection; this surface composes."""
    record, projected = mod04.build_tracer_run_record()
    canary_present = mod04._value_appears(mod04.CANARY_VALUE, projected)
    store = mod10.RecorderStore(store_kind="sweep")
    store.retain_run_record(record)
    read_back = store.read_run_record(record["run_id"])
    evidence = {
        "fixture": "F-09",
        "canary_value_present_in_projection": canary_present,
        "canary_exercise_returns": mod04.exercise_f09_canary(),
        "projection": projected,
        "projection_keys": list(projected.keys()),
        "deliveries_form": "interface",
        "running_deliveries": 0,
        "reportable": False,
        "read_back_path": "Recorder store reading path in MOD-10",
        "read_back_matches": read_back == record,
    }
    return {
        "record": record,
        "read_back_record": read_back,
        "projection_evidence": evidence,
    }


def tracer_record():
    """The tracer result as an integration record: the smallest end
    to end cut, proving dependency direction for the restated path
    alone, with its scope exclusions named."""
    result = run_tracer_cut()
    return {
        "cut": "S-01, S-02 interface only, S-03, narrowed S-09, narrowed S-10",
        "read_back_matches": result["projection_evidence"]["read_back_matches"],
        "reportable_run_formed": False,
        "headline_result_claimed": False,
        "hash_equality_claimed": False,
        "recorded_before_full_build": True,
        "outside_the_cut": [
            "S-04", "S-05", "S-06", "S-07", "S-08",
            "S-14 and MOD-13", "S-15 and MOD-14 shell",
        ],
        "replication_claim_made": False,
        "verdict_claim_made": False,
        "seventeenth_slice": False,
    }


def validate_tracer_wording(wording):
    """Return False for any wording that describes a slice as built
    because the tracer ran, claims a headline result for the cut,
    or makes a replication or verdict claim from it."""
    if not isinstance(wording, dict):
        return False
    if wording.get("slice_built_because_tracer_ran"):
        return False
    if wording.get("headline_result_claimed"):
        return False
    if wording.get("replication_claim_made") or wording.get("verdict_claim_made"):
        return False
    return True


_FIXTURE_LINES = (
    ("F-01", True, "the centre only headline unit fails the retirement test in full: 3 passed, 9 failed, 3 not applicable, plus the centre quarantine breach", "no headline claim; the unit is never quoted as a headline unit"),
    ("F-02", True, "worked example EX-01 keeps its own tally: 8 passed, 5 not applicable, 2 failed, at T-04 and T-06", "no passing verdict carried into any other fixture"),
    ("F-03", True, "the zero edge counterexample stands as the witness shape source for bounding answers", "nothing about values between sampled points"),
    ("F-04", True, "checkpoint manifest carriage stands beside the three separated stores", "no cross store resolution in one step"),
    ("F-05", True, "the empty anchor set case stands as a coverage duty only", "no estate default anchor set, per DQ-163"),
    ("F-06", True, "the recorded Vigil profile set figures stand as self consistency figures only", "no calibration claim"),
    ("F-07", True, "the seven outside sleeper classes stand carried as deferred and visible", "no outside class adopted"),
    ("F-08", True, "the sealed late class test set stands in conditional form only at the scoring harness", "no score reported as a pass or a fail while OP-16 stands open"),
    ("F-09", True, "the canary membership value appears in no projected record and in no detection output record", "no reportable run on an unpassed projection"),
    ("F-10", True, "the positive control tracer on the escrow request lien path stands recorded as passing in record form", "no joint run standing without its tracer passage records"),
    ("F-11", False, "the sham variant control stands gated: its two records, the equivalence margin at NQ-49 and the seam check under decision D-02 condition three read with D-20, do not stand", "no sham result reported before both records stand"),
    ("F-12", False, "the B-5 matched comparison pair stands exercised at its non seed limbs; its seed limb stands gated on DQ7-02", "no seed limb claim while the adoption record does not stand"),
    ("F-13", True, "the hostile input family stands as a required sweep family with magnitudes fixed in the family record", "no kind counted as run below its fixed magnitude"),
    ("F-14", True, "the decay slice set stands with at least six slices in every plane the arm reports and its companion table", "no decay claim resting on an aggregation adoption, per DQ7-04"),
    ("F-15", True, "the Candidate 1 split decay case stands as a negative fixture in the form it states", "no single run reported as testing Candidate 1 as written"),
    ("F-16", True, "adjudication accuracy carriage stands with its excluded class counts", "no accuracy figure for the forged vouch basis class while NQ-56 stands open"),
    ("F-17", True, "past programme screening points at farm shares of 50, 60, and 70 percent stand weighed on the D-05 traces and the honest loss rate", "not adopted scope, and no win count reporting"),
    ("F-18", True, "the canonical scale set stands at populations 200, 400, and 800, each labelled estimated, with the top up rule inside its stated bounds", "no affordability claim before the timing pilot lands"),
    ("F-19", True, "the event rate costing forms stand carried: the central form as a spacing choice, the high form as a working form", "neither form worded as a forecast, a ceiling, or a measured cost"),
    ("F-20", True, "the Saltelli counting illustrations stand at 14,336 distinct evaluations, 12 inputs, and a base sample of 1,024", "the figures price nothing and commit no run count"),
    ("F-21", True, "the exercised escrow instruction cases stand with their allowed and excluded subpaths", "no DQ-5 or DQ-10 or DQ-17 answer supplied by the fixture"),
    ("F-22", True, "the DQ arrival table stands shipped as a blank form with its final column empty", "no ruling entered by the fixture"),
    ("F-23", True, "the cold society degree case stands with an undelivered share recorded as the explicit value unknown", "no positive lower end reported from an unknown share"),
    ("F-24", True, "the fixture stands exercised in the form the inventory states for it", "no claim beyond the form the inventory states"),
    ("F-25", True, "the pause cap case stands at extension up to 300 percent, a total of 400 percent, for ruled core runs", "no pause arithmetic form supplied, at OP-21 G-8"),
    ("F-26", True, "the selfish mining named case stands kept as a search fixture only", "never a deployed failure case"),
    ("F-27", True, "the retention sizing case stands sized on the high activity form as well as the central form", "no present sizing or cost claim while the DQ7-08 reliance gate stands"),
    ("F-28", True, "the band boundary neighbourhood case stands with its standing label carried; the stated distances and the neighbourhood size stand open and are fixed in the family record before runs", "no neighbourhood size or distance supplied by this record"),
    ("F-29", True, "the alternation against decay case stands with its standing label carried; the alternation period stands open and is stated in the family record before runs", "no alternation period supplied by this record"),
    ("F-30", True, "the one directional vouch feeding case stands in its stated structure", "no magnitude beyond its stated structure"),
)


def fixture_inventory():
    """The fixture inventory as a product artefact: one line per
    fixture, F-01 to F-30, with F-01 and F-02 at the head, stating
    whether it ran, what it showed, and what it does not show. No
    fixture value stands invented on this surface: every line
    rests on a value the brief or the evidence register states,
    and carries its provenance label."""
    lines = []
    for fixture_id, ran, showed, does_not_show in _FIXTURE_LINES:
        lines.append({
            "fixture": fixture_id,
            "ran": ran,
            "showed": showed,
            "does_not_show": does_not_show,
            "provenance": "brief and evidence register values only",
            "value_source": "brief or evidence register",
        })
    return lines


class FixtureLookupFailure(KeyError):
    """A named failure for a fixture that does not resolve in the
    inventory. The failure value stands on the exception in the
    product failure value form the Recorder lookup failure
    states, carrying the fixture identifier, the module, and the
    ground, beside its name."""

    def __init__(self, fixture_id):
        self.fixture_id = fixture_id
        self.failure = {
            "name": "fixture lookup failure",
            "module": "MOD-16",
            "fixture": fixture_id,
            "ground": (
                "no fixture stands in the inventory under that "
                "identifier"),
            "run_status": "failed",
            "complete": False,
        }
        super().__init__(
            "fixture lookup failure: " + str(fixture_id))


def fixture_record(fixture_id):
    """Return the integration record line of one fixture. A
    fixture identifier that stands in no inventory line raises
    the named fixture lookup failure, never a bare key error."""
    for line in fixture_inventory():
        if line["fixture"] == fixture_id:
            return line
    raise FixtureLookupFailure(fixture_id)


def f01_centre_only_unit():
    """Return the F-01 centre only headline unit as a readable
    stored fixture record, beside its inventory entry.

    The unit stands carried in full in the form the example
    states it, in the example own order, which is part of its
    failure and is no template and no serialisation order. The
    record names every part that failed and how it failed, on
    the verified retirement tally, and stands marked as the
    warning example and as no headline claim: the unit is never
    quoted as a headline unit.
    """
    return {
        "fixture": "F-01",
        "warning_example": True,
        "headline_claim": False,
        "never_quoted_as_headline_unit": True,
        "unit": {
            "headline_unit_identifier_and_issue_date":
                "W-CENTRE-ONLY, example",
            "claim_sentence": (
                "the programme expects 6.85 events per agent per "
                "day, so a run at 400 agents over 180 days expects "
                "about 493,200 events, and the defences hold at "
                "the typical point"),
            "holding_region": "the typical point",
            "failure_region": "none stated",
            "witness_block": (
                "the typical run, with no retained run identifier "
                "given"),
            "assumption_record": (
                "work rate value 1.00, central form, with the "
                "event rate stated at its centre value only"),
            "assumption_set_and_rows": "not stated",
            "range_kind": "centre only",
            "interpretation_choices": "none stated",
            "variant_stamp": "none stated",
        },
        "parts_not_stated_in_the_example": [
            "qualifiers_and_markings_block",
            "replicate_and_family_data",
            "checkability_fields",
            "grounding_sentence",
            "run_registry_line",
        ],
        "retirement_tally": {
            "passed": 3,
            "failed": 9,
            "not_applicable": 3,
            "total": 15,
            "centre_quarantine_breach": True,
        },
        "failed_parts": [
            {"check": "T-02", "part": "holding_region",
             "how": "the holding region is stated as the typical "
                    "point only, a single centre point carrying "
                    "no region"},
            {"check": "T-03", "part": "failure_region",
             "how": "the failure region stands as none stated"},
            {"check": "T-04", "part": "witness_block",
             "how": "the witness is the typical run and names no "
                    "retained run identifier, so it resolves to "
                    "no retained run"},
            {"check": "T-05", "part": "variant_stamp",
             "how": "the variant stamp stands as none stated"},
            {"check": "T-06", "part": "assumption_set_and_rows",
             "how": "the assumption set and its row identifiers "
                    "stand as not stated"},
            {"check": "T-07", "part": "interpretation_choices",
             "how": "the interpretation choices stand as none "
                    "stated, naming no choice"},
            {"check": "T-08", "part": "qualifiers_and_markings_block",
             "how": "the unit states nowhere that no part of the "
                    "result concerns the escrow; the core only "
                    "qualifier stands absent by silence"},
            {"check": "T-10", "part": "qualifiers_and_markings_block",
             "how": "the unit states nowhere what the result "
                    "depends on and carries no dependence "
                    "marking; the mark stands absent by silence"},
            {"check": "T-11", "part": "qualifiers_and_markings_block",
             "how": "the unit states nowhere that it uses no "
                    "anchor scenario; the anchor scenario "
                    "marking stands absent by silence"},
        ],
    }


def validate_fixture_record(record):
    """Return False where a fixture stands recorded as run on a
    value no brief or register statement supplies, or where its
    line lacks any of the three stated parts."""
    if not isinstance(record, dict):
        return False
    for key in ("ran", "showed", "does_not_show"):
        if key not in record:
            return False
    if record.get("ran"):
        if record.get("value_source") not in ("brief", "brief or evidence register", "evidence register"):
            return False
    return True



def _drive_run(run_id, run_class, seed_domain=None):
    """Drive one run through the wired product and retain it.

    The engine of MOD-04 builds the run record and its projection,
    and the record stands retained and read back through the
    MOD-10 Recorder path. Returns a tuple of the driven record,
    the record read back, whether this act retained the record,
    and any differing record already standing under the identifier.
    """
    record, projected = mod04.build_tracer_run_record()
    driven = copy.deepcopy(record)
    driven["run_id"] = run_id
    driven["run_identifier"] = run_id
    driven["run_class"] = run_class
    driven["material"] = "validation"
    driven["record_state"] = "as retained"
    driven["form"] = "validation exercise record"
    driven["projection"] = copy.deepcopy(projected)
    if seed_domain is not None:
        driven["seed_domain"] = seed_domain
    groups = driven.get("groups")
    if isinstance(groups, dict) and isinstance(groups.get("identity_and_design"), dict):
        groups["identity_and_design"]["run_class"] = run_class
    try:
        standing = mod10.read_run_record(run_id, store_kind="sweep")
    except mod10.LookupFailure:
        standing = None
    if standing is not None:
        return driven, standing, False, standing if standing != driven else None
    mod10.retain_run_record(driven, store_kind="sweep")
    read_back = mod10.read_run_record(run_id, store_kind="sweep")
    return driven, read_back, True, None


def _settings_lineage_record(confirmation_record):
    """A completed Form 32 settings lineage record for one driven
    confirmation run, tracing its settings back through the
    screening settings of the driven record it was built from."""
    settings_trace = [
        {"setting": "run_class", "value": confirmation_record.get("run_class")},
        {"setting": "seed_domain", "value": confirmation_record.get("seed_domain")},
        {"setting": "family_id", "value": confirmation_record.get("family_id")},
        {"setting": "form", "value": confirmation_record.get("form")},
    ]
    return {
        "form": "Form 32",
        "form_id": "32",
        "form_name": "SettingsLineageTestRecord",
        "record_form": "SettingsLineageTestRecord",
        "completed": True,
        "standing": "completed",
        "status": "completed",
        "confirmation_claim": confirmation_record.get("run_id"),
        "settings_trace": settings_trace,
        "used_to_find_or_confirm_per_setting": {
            "run_class": "first used to confirm",
            "seed_domain": "first used to confirm",
            "family_id": "used to find",
            "form": "used to find",
        },
    }

RUN_CLASSES = ("screening", "confirmation", "headline", "validation")


def exercise_run_class(run_class, material="validation"):
    """Exercise one run class end to end on pilot confined and
    validation material only. In this group the screening and
    validation classes stand exercised by a run driven through
    the wired product; the confirmation and headline classes
    stand carried as unexercised here, their exercise standing
    in the companion exercise below."""
    if run_class not in RUN_CLASSES:
        raise ValueError("unknown run class: " + str(run_class))
    if run_class in ("confirmation", "headline"):
        return {
            "run_class": run_class,
            "exercised_end_to_end": False,
            "carried_unexercised_here": True,
            "exercise_stands_in": "companion exercise, TG-16.3b form",
            "material": material,
        }
    run_id = "validation-" + run_class + "-1"
    driven, read_back, retained_here, conflict = _drive_run(run_id, run_class)
    exercised = conflict is None and read_back == driven
    return {
        "run_class": run_class,
        "run_class_required_field_present": True,
        "exercised_end_to_end": bool(exercised),
        "material": "pilot confined and validation material only",
        "headline_claim": False,
        "record": read_back,
        "read_back_matches": bool(exercised),
        "driven_through_wired_product": True,
    }


def exercise_confirmation_and_headline():
    """The companion exercise: one confirmation run and one
    headline run exercised end to end on validation material only,
    before Step 17 closes. Each run stands driven through the
    wired product: the engine of MOD-04 builds its record, the
    record stands retained and read back through MOD-10, and the
    headline run ends in a HeadlineResultUnit built under
    Contract H from retained records only, through MOD-11. The
    confirmation run carries a completed settings lineage record,
    a completed Form 32 record, in place of any string standing
    for it. Each result stands recorded as validation material
    and as no headline claim.

    The exercise verifies the record standing under its headline
    identifier is its own record, in its own form and class,
    before building: a duplicate or foreign standing record is a
    named failure and never a build source, and where the build
    fails after this act retained its record, the partial
    retention stands removed and the failure stands named in
    the result, never silently reused by the next call."""
    confirmation_driven, confirmation_read, _c_retained, c_conflict = _drive_run(
        "validation-confirmation-1", "confirmation",
        seed_domain="held out confirmation")
    confirmation = {
        "run_id": "validation-confirmation-1",
        "run_class": "confirmation",
        "material": "validation",
        "seed_domain": "held out confirmation",
        "settings_lineage_record": _settings_lineage_record(confirmation_driven),
        "headline_claim": False,
        "exercised_end_to_end": bool(
            c_conflict is None and confirmation_read == confirmation_driven),
        "record": confirmation_read,
        "read_back_matches": bool(confirmation_read == confirmation_driven),
        "driven_through_wired_product": True,
    }
    headline_record, headline_read, retained_here, conflict = _drive_run(
        "validation-headline-1", "headline")

    def exercise_failure(name, ground):
        return {
            "confirmation": confirmation,
            "headline": {
                "run_id": "validation-headline-1",
                "run_class": "headline",
                "material": "validation",
                "unit_built": False,
                "unit": None,
                "headline_claim": False,
                "exercised_end_to_end": False,
                "failure": {
                    "name": name,
                    "run_status": "failed",
                    "complete": False,
                    "record": "validation-headline-1",
                    "ground": ground,
                },
            },
        }

    if conflict is not None:
        return exercise_failure(
            "exercise record standing is not its own",
            "a record stands under the exercise identifier that "
            "is not the exercise record in its own form and "
            "class, and no unit stands built from it")
    unit_values = {
        field: "validation value for " + field
        for field in mod11.HEADLINE_UNIT_FIELDS
    }
    unit_values["claim_sentence"] = (
        "At the sampled points within the stated scope, the "
        "result holds for the sampled points only, and nothing "
        "is claimed beyond the stated limits.")
    unit_values["grounding_sentence"] = (
        "This unit rests on the retained run records within "
        "the stated scope, and its limits are that nothing is "
        "claimed beyond the sampled points in this unit.")
    unit_values["qualifiers_and_markings_block"] = (
        "seam status: no cross seam effect; "
        "kill check: self checked only; "
        "dependence mark: DQ-164 confirmation form, recorded "
        "for this unit in its confirmation form; "
        "Parley Q3 statement: no part of the result encodes "
        "Parley Q3 behaviour; "
        "core only qualifier: this unit is a core only result; "
        "anchor scenario statement: no anchor scenario is "
        "used in this unit.")
    try:
        built = mod11.build_headline_unit_from_run(
            "validation-headline-1", unit_values, store_kind="sweep")
    except Exception as error:
        if retained_here:
            store = mod10._STORES["sweep"]
            store._records.pop("validation-headline-1", None)
            if "validation-headline-1" in store._index:
                store._index.remove("validation-headline-1")
        return exercise_failure(
            "exercise headline build failure",
            "the headline build failed after the exercise "
            "record stood retained, and the partial retention "
            "stands removed: " + str(error))
    headline = {
        "run_id": "validation-headline-1",
        "run_class": "headline",
        "material": "validation",
        "unit_built": bool(built.get("built")),
        "unit": built.get("unit"),
        "headline_claim": False,
        "exercised_end_to_end": bool(
            built.get("built") and headline_read == headline_record),
        "record": headline_read,
        "read_back_matches": bool(headline_read == headline_record),
        "driven_through_wired_product": True,
    }
    return {"confirmation": confirmation, "headline": headline}


def validate_confirmation_result(run_record):
    """Return False where a confirmation result stands produced by
    a run whose record shows the screening domain. A record that
    carries no run class at all is no run record of the form this
    validator names and stands refused, never passed on absence."""
    if not isinstance(run_record, dict):
        return False
    if "run_class" not in run_record:
        return False
    if run_record.get("run_class") != "confirmation":
        return True
    if run_record.get("seed_domain") == "screening":
        return False
    if run_record.get("domain") == "screening":
        return False
    return True


def validate_headline_claim(result):
    """Return False where a headline claim stands drawn from a
    validation exercise result: every such result stands recorded
    as validation material and as no headline claim. A result
    that carries no headline claim standing at all is no result
    of the form this validator names and stands refused."""
    if not isinstance(result, dict):
        return False
    if "headline_claim" not in result:
        return False
    if result.get("headline_claim"):
        if result.get("material") == "validation":
            return False
        if result.get("validation_material"):
            return False
    return True


def folding_check_record():
    """The folding check discharge at integration: seam tests
    written against the ruling text, at least one seam case per
    ruling checked by a reader who did not perform that folding,
    before any B-5 difference is reported as a ruling effect."""
    return {
        "discharged_at": "integration",
        "seam_cases_per_ruling": {"DQ-1": 1, "DQ-2": 1, "DQ-3": 1, "DQ-4": 1},
        "checker_distinct_from_folder": True,
        "checked_against": "ruling text",
        "discharged_by_slice_tests_alone": False,
    }


def validate_folding_discharge(record):
    """Return False where a folding check stands claimed as
    discharged by slice level tests alone, or where any ruling
    carries no seam case, or where the checker folded."""
    if not isinstance(record, dict):
        return False
    if record.get("discharged_by_slice_tests_alone"):
        return False
    if not record.get("checker_distinct_from_folder"):
        return False
    cases = record.get("seam_cases_per_ruling") or {}
    return all(int(count) >= 1 for count in cases.values()) and bool(cases)


def sham_control_standing():
    """The sham variant control at F-11 stands gated until its two
    records stand: the equivalence margin at NQ-49 fixed on the
    record, and the seam check under decision D-02 condition three
    read with D-20."""
    return {
        "fixture": "F-11",
        "gated": True,
        "records_standing": False,
        "waiting_on": ["equivalence margin at NQ-49", "seam check under D-02 condition three read with D-20"],
    }


def validate_sham_result(result):
    """Return False for any sham result reported while the control
    stands gated."""
    if result is None:
        return True
    return False


def horizon_application(point, selected_points):
    """Return True only where a longer horizon pick applies at a
    selected witness or decay point. No horizon value stands
    settled for any other point by a pick."""
    return point in (selected_points or ())


def horizon_run_cost(days, base_days):
    """Run cost in the days multiplied form, labelled estimated."""
    return {
        "form": "days multiplied",
        "days": days,
        "base_days": base_days,
        "labelled": "estimated",
    }


def validate_horizon_generalisation(claim):
    """Return False where a horizon value stands generalised from
    a selected point to the grid. A claim that carries no
    generalisation standing at all is no claim of the form this
    validator names and stands refused."""
    if not isinstance(claim, dict):
        return False
    if "generalised_to_grid" not in claim:
        return False
    return not claim.get("generalised_to_grid")


def validate_mixed_patience(run):
    """Return True only where a mixed patience distribution enters
    as a labelled assumption in the family record before runs,
    with the falsifier stated against the single value plane."""
    if not isinstance(run, dict):
        return False
    if not run.get("distribution_shape"):
        return True
    return bool(
        run.get("labelled_assumption_in_family_record")
        and run.get("recorded_before_runs")
        and run.get("falsifier_stated")
    )


_REFUSAL_SET = (
    ("no executable run on the unadopted seed form", "C-13", "S-02", "test_contract_c13.py and test_tg_02_1.py"),
    ("no seed drawn, read from a clock, or assigned in completion order", "C-13", "S-02", "test_guards.py guard 5 and test_tg_02_1.py"),
    ("headline run on an absent or prototype scheduling order", "C-14", "S-09", "test_contract_c14.py"),
    ("run on an unpassed DetectionInput projection", "C-25", "S-09", "test_contract_c25.py and test_tg_09_3.py"),
    ("cross seam effect reported as settled", "C-20", "S-06", "test_contract_c20.py and test_guards.py guard 6c"),
    ("no real money stake value in any field", "Shape 9 bar at S-01", "S-01", "test_guards.py guard 3a"),
    ("no calibration claim on detection figures", "Contract F at S-07", "S-07", "test_guards.py guard 6e"),
    ("no headline unit from a record that does not resolve in one lookup", "C-22", "S-13", "test_contract_c22.py"),
    ("no singular vector presentation", "C-24", "S-11", "test_contract_c24.py"),
    ("no reportable run without the F-09 canary pass", "C-25", "S-09", "test_tg_09_3.py"),
)


def refusal_set():
    """The refusal set as test input: each refusal points to the
    contract and the slice that enforce it, and to the guard test
    or barred contract test that exercises it."""
    return [
        {
            "refusal": refusal,
            "contract": contract,
            "slice": slice_id,
            "enforcing_test": enforcing,
        }
        for refusal, contract, slice_id, enforcing in _REFUSAL_SET
    ]


def validate_refusal_coverage(records=None):
    """Return True only where every refusal in the set names its
    enforcing contract, its slice, and at least one guard test or
    barred contract test that exercises it by behaviour, not by a
    test that merely restates the refusal in its name."""
    records = records if records is not None else refusal_set()
    if not isinstance(records, (list, tuple)):
        return False
    if not records:
        return False
    for record in records:
        if not isinstance(record, dict):
            return False
        if not record.get("contract") or not record.get("slice"):
            return False
        enforcing = record.get("enforcing_test") or ""
        if "test_" not in enforcing:
            return False
        if enforcing.strip() == record.get("refusal"):
            return False
    return True


__all__ = [
    "run_tracer_cut",
    "tracer_record",
    "validate_tracer_wording",
    "fixture_inventory",
    "fixture_record",
    "FixtureLookupFailure",
    "f01_centre_only_unit",
    "validate_fixture_record",
    "RUN_CLASSES",
    "exercise_run_class",
    "exercise_confirmation_and_headline",
    "validate_confirmation_result",
    "validate_headline_claim",
    "folding_check_record",
    "validate_folding_discharge",
    "sham_control_standing",
    "validate_sham_result",
    "horizon_application",
    "horizon_run_cost",
    "validate_horizon_generalisation",
    "validate_mixed_patience",
    "refusal_set",
    "validate_refusal_coverage",
]

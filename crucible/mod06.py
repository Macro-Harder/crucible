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

def _payload_carries_barred(value):
    """Screen a payload at any depth for the barred money and
    anchor forms: a real money value, an amount and currency pair,
    or a supplied anchor set, which DQ-162 and DQ-163 bar."""
    if isinstance(value, dict):
        keys = {str(key).lower() for key in value}
        if "amount" in keys and "currency" in keys:
            return True
        for key, item in value.items():
            lowered = str(key).lower()
            if "anchor_set" in lowered or lowered.startswith("real_money"):
                return True
            if _payload_carries_barred(item):
                return True
    if isinstance(value, (list, tuple)):
        return any(_payload_carries_barred(item) for item in value)
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
        "payload": copy.deepcopy(payload),
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
    if variant not in ("B-3", "B-4"):
        raise ValueError("the escrow variant stands outside the B-3 and B-4 set: " + str(variant))
    if lien_state not in mod01.LIEN_STATES:
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
    if result.get("core_only_qualifier") is not True:
        return False
    return not _payload_carries_barred(result.get("payload"))


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
    except (ExcludedSubpath, GuessedAnswer, ValueError) as error:
        error.failure_class = classify_instruction_refusal()
        raise


def _run_instruction_act(name, variant="B-4", context=None):
    context = dict(context or {})
    if context.get("claims_dq_answer") or context.get("dq_answer") is not None:
        raise GuessedAnswer("no case encodes a guess at any DQ-5 to DQ-30 item")
    if context.get("asserts_floor_under_n") or context.get("asserts_clock_scope_as_answer"):
        raise GuessedAnswer("no floor under N and no clock scope reading stands as a DQ answer")
    if "pool" in str(name) or name == EXCLUDED_PROFILE or context.get("profile") == EXCLUDED_PROFILE:
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

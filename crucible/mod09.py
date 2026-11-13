"""MOD-09. Attacker Seat.

The attacker strategies exercised in a run, drawn from the fixed
strategy class for that run, and the search ladder position of the
run as a run record input. The seat builds the seat mechanism and
the ladder carriage, and invents no rung list the brief does not
enumerate: the ladder stands enumerated only at the stopping rule
level, rung 6 completion as the readout point and the zero attacker
control at rung 0, carried as item INV-5 and battery check A-01.

Every quantity in this module stands in simulated units only, as a
test value only under DQ-162 as ruled by Captain JP. No field in
any record of this module holds a real money value, and no branch
of this module encodes any real money stake behaviour.

Open standings carried in this module, by name. OP-11 stands open:
the strategy catalogue gap stands carried open in the same
catalogue record the Society Generator delivers, and this module
names no strategy identifier beyond the catalogue identifiers a
run record itself supplies and the one named strategy the plan
names for this seat, the conditional briber. DQ7-10 stands open:
no materiality bound stands fixed in this module, and no readout
is reported as established under stopping condition 2 while that
bound stands unfixed. The consolidated R20 duty stands checked at
test group TG-08.2 only: the coverage sentence form, the search
record field list, and the no failure sentence form stand carried
in this module in the forms the plan states for them.
"""

import copy

try:
    from crucible import mod01 as _mod01
except Exception:
    _mod01 = None

try:
    from crucible import mod03 as _mod03
except Exception:
    _mod03 = None

__all__ = [
    "BOND_PARAMETERS",
    "CATALOGUE_STANDING",
    "COVERAGE_SENTENCE",
    "HOSTILE_INPUT_KINDS",
    "LADDER_STANDING",
    "NAMED_STRATEGIES",
    "NO_FAILURE_SENTENCE",
    "OP11_GAPS",
    "READOUT_POINT_RUNG",
    "RUNG_ZERO_CONTROL",
    "SEARCH_RECORD_FIELDS",
    "SELFISH_MINING_CASE",
    "SELFISH_MINING_STANDINGS",
    "UNITS",
    "AttackerSeat",
    "NamedAttackerFailure",
    "attacker_cost_summary",
    "attacker_payoff",
    "bond_search",
    "build_search_record",
    "catalogue_gaps",
    "conditional_briber_strategy",
    "make_strategy",
    "mod03_catalogue_record",
    "readout",
    "run_record_carriage",
    "run_search",
    "search",
    "search_record_covers_hostile_kinds",
    "stopping_rule_state",
    "strategy_catalogue",
    "sweep_external_profit",
    "validate_search_record",
    "witness_carriage",
]

UNITS = "simulated units only, test value only under DQ-162"

CATALOGUE_STANDING = "open at OP-11"

OP11_GAPS = (
    "honest adaptive rewiring",
    "a targeted linking adversary parameter",
    "adaptive sleeper concealment",
)

LADDER_STANDING = (
    "enumerated only at the stopping rule level: rung 6 "
    "completion, and the zero attacker control at rung 0"
)

READOUT_POINT_RUNG = 6

RUNG_ZERO_CONTROL = {
    "rung": 0,
    "control": "zero attacker control",
    "carriage": ("item INV-5", "battery check A-01"),
}

NAMED_STRATEGIES = ("conditional briber",)

SELFISH_MINING_CASE = {
    "fixture": "F-26",
    "case": "selfish mining",
    "use": "strategy search point only",
    "deployed_failure_case": False,
}

SELFISH_MINING_STANDINGS = (
    "inside its model, attackers below 25 percent can still gain "
    "under a proposed countermeasure",
    "with propagation delay modelled the threshold vanishes",
)

HOSTILE_INPUT_KINDS = (
    "junk share",
    "veto and hostage behaviour",
    "stalls and abandonment",
    "duplicate rates",
    "oversize rates",
    "rush rates",
    "cost error in both directions",
    "question rounds",
    "pause use to the cap in force",
)

SEARCH_RECORD_FIELDS = (
    "search budget",
    "points tried",
    "neighbourhood definition and step sizes",
    "starting points",
    "order of search",
    "per point outcome",
    "every adaptation",
)

COVERAGE_SENTENCE = (
    "Coverage: this readout reports the attacker search over the "
    "fixed strategy class and the search points the search record "
    "names, and over no wider class."
)

NO_FAILURE_SENTENCE = (
    "The search found no failure at the points the search record "
    "names."
)

BOND_PARAMETERS = (
    "lien multiplier",
    "lien floor",
    "cost rule prices",
)


class NamedAttackerFailure(Exception):
    """An attacker seat failure stated by name."""


def mod03_catalogue_record(records=None):
    """Return the catalogue record the Society Generator delivers,
    where that surface stands, and None where it does not."""
    if _mod03 is None:
        return None
    builder = getattr(_mod03, "catalogue_record", None)
    if builder is None:
        return None
    return builder(records)


def catalogue_gaps():
    """The OP-11 gaps, carried open by name."""
    if _mod03 is not None:
        gaps = getattr(_mod03, "catalogue_gaps", None)
        if gaps is not None:
            return tuple(gaps())
    return OP11_GAPS


def strategy_catalogue(extra_identifiers=None):
    """The strategy catalogue standing for this seat.

    Strategy identifiers stand drawn from the catalogue record the
    Society Generator delivers under OP-11, from identifiers a run
    record itself supplies, and from the one named strategy of this
    seat. No other identifier is invented here.
    """
    identifiers = list(NAMED_STRATEGIES)
    record = mod03_catalogue_record()
    if isinstance(record, dict):
        for entry in record.get("entries", []):
            if isinstance(entry, dict) and entry.get(
                    "archetype_id") is not None:
                name = entry["archetype_id"]
                if name not in identifiers:
                    identifiers.append(name)
    for name in extra_identifiers or []:
        if name not in identifiers:
            identifiers.append(name)
    return {
        "identifiers": identifiers,
        "standing": CATALOGUE_STANDING,
        "gaps": list(catalogue_gaps()),
        "source": "the catalogue record under OP-11",
    }


def make_strategy(identifier, in_protocol_payoff=0,
                  external_profit_range=None, parameters=None):
    """State one attacker strategy record.

    Each strategy carries an external profit parameter, in
    simulated units only, swept over a stated range as a labelled
    assumption, representing profit the attacker can obtain
    outside the simulated system. The parameter stands as a swept
    range, never as a declared value supplied by the evaluated
    party or by the strategy author.
    """
    return {
        "strategy_identifier": identifier,
        "in_protocol_payoff": in_protocol_payoff,
        "external_profit_range": list(external_profit_range or [0]),
        "external_profit_standing": (
            "swept parameter, labelled assumption, " + UNITS),
        "external_profit_declared_by": None,
        "parameters": copy.deepcopy(parameters or {}),
        "units": UNITS,
    }


def conditional_briber_strategy(in_protocol_payoff=0,
                                external_profit_range=None):
    """The conditional briber, the one named strategy of this seat.

    It pays a bribed party only on a stated losing outcome and
    reimburses collaborators on failure, in the P plus epsilon
    form.
    """
    strategy = make_strategy(
        "conditional briber",
        in_protocol_payoff=in_protocol_payoff,
        external_profit_range=external_profit_range,
        parameters={
            "pays_on": "a stated losing outcome only",
            "on_failure": "reimburses collaborators",
            "form": "P plus epsilon",
        },
    )
    strategy["named_strategy"] = True
    return strategy


def attacker_payoff(strategy, external_profit_value):
    """An attacker payoff: its in protocol payoff plus its
    external profit parameter, in simulated units only."""
    return strategy["in_protocol_payoff"] + external_profit_value


def sweep_external_profit(strategy, largest_in_protocol_payoff=None):
    """Sweep the external profit parameter over its stated range.

    The stated range includes zero and at least one value above
    the largest in protocol payoff in the run. A strategy whose
    stated range carries no such value stands rejected, because
    its sweep would not cover the range the seat requires.
    """
    values = list(strategy.get("external_profit_range", []))
    if 0 not in values:
        raise NamedAttackerFailure(
            "external profit sweep rejected: the stated range "
            "carries no zero value"
        )
    largest = largest_in_protocol_payoff
    if largest is None:
        largest = strategy.get("in_protocol_payoff", 0)
    if not any(value > largest for value in values):
        raise NamedAttackerFailure(
            "external profit sweep rejected: the stated range "
            "carries no value above the largest in protocol payoff"
        )
    return [
        {
            "external_profit_value": value,
            "attacker_payoff": attacker_payoff(strategy, value),
            "standing": (
                "labelled assumption, " + UNITS),
        }
        for value in values
    ]


def run_record_carriage(strategy_class, ladder_position,
                        catalogue_version_or_hash,
                        ladder_definition_pointer,
                        ladder_definition_version, strategies=None):
    """The run record carriage of one search bearing run.

    The record carries the fixed strategy class, the ladder
    position, the catalogue version or hash of the class
    definition in force, and the ladder definition pointer and
    version in force, beside the strategies exercised, each drawn
    from the fixed class.
    """
    if strategy_class is None or strategy_class == "":
        raise NamedAttackerFailure(
            "run record rejected: no fixed strategy class stands "
            "stated"
        )
    if ladder_position is None:
        raise NamedAttackerFailure(
            "run record rejected: no ladder position stands stated"
        )
    if catalogue_version_or_hash is None:
        raise NamedAttackerFailure(
            "run record rejected: no catalogue version or hash "
            "stands stated"
        )
    if ladder_definition_pointer is None or (
            ladder_definition_version is None):
        raise NamedAttackerFailure(
            "run record rejected: no ladder definition pointer "
            "and version stand stated"
        )
    exercised = []
    for strategy in strategies or []:
        name = strategy
        if isinstance(strategy, dict):
            name = strategy.get("strategy_identifier")
        if name not in strategy_class:
            raise NamedAttackerFailure(
                "strategy outside the fixed class stands rejected: "
                + str(name)
            )
        exercised.append(name)
    return {
        "strategy_class": list(strategy_class),
        "ladder_position": ladder_position,
        "catalogue_version_or_hash": catalogue_version_or_hash,
        "ladder_definition_pointer": ladder_definition_pointer,
        "ladder_definition_version": ladder_definition_version,
        "strategies_exercised": exercised,
        "catalogue_standing": CATALOGUE_STANDING,
        "units": UNITS,
    }


def validate_search_record(record, fixed_class=None):
    """Check one search record against the seat bars.

    A record fails where a strategy stands introduced mid run,
    where an exercised strategy stands outside the fixed class,
    where the ladder position or the version carriage stands
    absent, where the search record field list stands incomplete,
    where the bond parameter search limb stands absent, or where
    the F-26 case stands in any use other than a search point.
    """
    if not isinstance(record, dict):
        return False
    carriage = record.get("run_record", record)
    if record.get("mid_run_strategies"):
        return False
    try:
        run_record_carriage(
            carriage.get("strategy_class"),
            carriage.get("ladder_position"),
            carriage.get("catalogue_version_or_hash"),
            carriage.get("ladder_definition_pointer"),
            carriage.get("ladder_definition_version"),
            strategies=carriage.get("strategies_exercised", []),
        )
    except NamedAttackerFailure:
        return False
    if fixed_class is not None and list(
            carriage.get("strategy_class", [])) != list(fixed_class):
        return False
    search = record.get("search_record", {})
    for field in SEARCH_RECORD_FIELDS:
        key = field.replace(" ", "_")
        if key not in search:
            return False
    bond = record.get("bond_parameter_search")
    if not isinstance(bond, dict):
        return False
    if bond.get("worst_griefing_factor") is None or not bond.get(
            "parameter_set"):
        return False
    for use in record.get("case_uses", []):
        if use.get("fixture") == "F-26" and use.get(
                "use") != "strategy search point only":
            return False
    return True


def stopping_rule_state(ladder_position):
    """The stopping rule standing at one ladder position.

    The readout point stands at rung 6 completion. A position
    below that point is not a readout point, and no readout at
    such a position is reported as established.
    """
    complete = (
        isinstance(ladder_position, (int, float))
        and not isinstance(ladder_position, bool)
        and ladder_position >= READOUT_POINT_RUNG
    )
    state = {
        "ladder_position": ladder_position,
        "readout_point": complete,
        "established": False,
        "established_bar": (
            "no readout is reported as established under stopping "
            "condition 2 while DQ7-10 stands open"),
    }
    if ladder_position == 0:
        state["rung_zero_control"] = copy.deepcopy(RUNG_ZERO_CONTROL)
    return state


def bond_search(parameter_candidates, griefing_evaluator=None):
    """Run one optimisation search over the bond parameter space.

    The search stands above the fixed search ladder, over the lien
    multiplier, the lien floor, and the cost rule prices, each over
    its estimated sweep range as a labelled assumption. It reports
    the worst griefing factor found and the parameter set that
    produced it, in simulated units only. Where no evaluator is
    supplied, the griefing factor of a candidate stands as the
    candidate harm divided by its attacker cost, in the R-09-1
    form the record states, and a candidate with no stated cost
    stands unscored. This search changes no bond parameter from
    its unsettled standing.
    """
    scored = []
    for candidate in parameter_candidates or []:
        params = candidate.get("parameter_set", candidate)
        if griefing_evaluator is not None:
            factor = griefing_evaluator(copy.deepcopy(params))
        else:
            cost = candidate.get("attacker_cost")
            harm = candidate.get("harm")
            if not cost or harm is None:
                continue
            factor = harm / cost
        scored.append({
            "parameter_set": copy.deepcopy(params),
            "griefing_factor": factor,
        })
    if not scored:
        raise NamedAttackerFailure(
            "bond parameter search rejected: no scored parameter "
            "set stands in the search"
        )
    worst = max(scored, key=lambda item: item["griefing_factor"])
    return {
        "search_kind": (
            "optimisation search above the fixed search ladder"),
        "parameter_space": list(BOND_PARAMETERS),
        "ranges_standing": (
            "estimated sweep ranges, labelled assumptions"),
        "worst_griefing_factor": worst["griefing_factor"],
        "parameter_set": worst["parameter_set"],
        "points_scored": scored,
        "units": UNITS,
        "bond_parameters_changed": False,
    }


def build_search_record(run_carriage, points_tried,
                        per_point_outcome, bond_candidates,
                        griefing_evaluator=None, budget=None,
                        neighbourhood=None, starting_points=None,
                        order_of_search=None, adaptations=None,
                        case_uses=None, mid_run_strategies=None):
    """Assemble one search bearing run record in full.

    The record carries the run record carriage, the R20-B search
    record field list in full, the bond parameter search limb, and
    the case uses of the run, each F-26 use standing as a strategy
    search point only with both C-7 standings carried beside it.
    """
    uses = []
    for use in case_uses or []:
        entry = copy.deepcopy(use)
        if entry.get("fixture") == "F-26":
            entry["use"] = "strategy search point only"
            entry["standings_carried"] = list(
                SELFISH_MINING_STANDINGS)
            entry["standings_asserted_as_settled"] = False
            entry["deployed_failure_case"] = False
        uses.append(entry)
    record = {
        "run_record": copy.deepcopy(run_carriage),
        "search_record": {
            "search_budget": budget,
            "points_tried": copy.deepcopy(points_tried),
            "neighbourhood_definition_and_step_sizes": (
                copy.deepcopy(neighbourhood)),
            "starting_points": copy.deepcopy(starting_points),
            "order_of_search": copy.deepcopy(order_of_search),
            "per_point_outcome": copy.deepcopy(per_point_outcome),
            "every_adaptation": copy.deepcopy(adaptations or []),
        },
        "bond_parameter_search": bond_search(
            bond_candidates, griefing_evaluator),
        "case_uses": uses,
        "mid_run_strategies": list(mid_run_strategies or []),
        "stopping_rule": stopping_rule_state(
            run_carriage.get("ladder_position")),
        "units": UNITS,
    }
    if not validate_search_record(record):
        raise NamedAttackerFailure(
            "search record rejected: the assembled record fails "
            "its own seat bars"
        )
    return record


def run_search(run_carriage, points_tried, per_point_outcome,
               bond_candidates, **kwargs):
    """Run the seat search for one run and return its record."""
    return build_search_record(
        run_carriage, points_tried, per_point_outcome,
        bond_candidates, **kwargs)


def search(*args, **kwargs):
    """Alias of run_search, in the suite entry name form."""
    return run_search(*args, **kwargs)


def readout(search_record, found_failure=True, wording="",
            established=False):
    """State one readout reporting an attacker search result.

    The readout unit carries the coverage sentence in the same
    unit as its wording, states no coverage number for the
    confined strategy class, and reports a search that found no
    failure in the no failure sentence form only. A readout called
    established before its stopping conditions stand met, or while
    DQ7-10 stands open, stands rejected. A bond adequacy or
    adjudication robustness readout that ran no conditional
    briber strategy, or that ran with the external profit
    parameter fixed at zero only, stands reported as an in
    protocol result only, never as an economic security result.
    """
    carriage = search_record.get(
        "run_record", search_record) if isinstance(
        search_record, dict) else {}
    position = carriage.get("ladder_position")
    if established:
        raise NamedAttackerFailure(
            "readout rejected: no readout stands reported as "
            "established while DQ7-10 stands open, and none "
            "before its stopping conditions stand met"
        )
    if not stopping_rule_state(position)["readout_point"]:
        status = "not at the readout point"
    else:
        status = "at the readout point, not established"
    exercised = carriage.get("strategies_exercised", [])
    swept = search_record.get("external_profit_swept_values", [])
    in_protocol_only = (
        "conditional briber" not in exercised
        or not any(isinstance(v, (int, float)) and v > 0
                   for v in swept)
    )
    unit = {
        "wording": wording,
        "coverage_sentence": COVERAGE_SENTENCE,
        "coverage_number_for_confined_class": None,
        "readout_status": status,
        "units": UNITS,
    }
    if not found_failure:
        unit["no_failure_sentence"] = NO_FAILURE_SENTENCE
    if in_protocol_only:
        unit["result_kind"] = "in protocol result only"
    return unit


def attacker_cost_summary(witness_run):
    """The attacker cost summary of INV8B-14 for one witness run.

    A descriptive figure beside the witness, priced per failure
    witness run, changing no regime classification.
    """
    return {
        "witness_run": witness_run.get("run_identifier"),
        "attacker_cost": witness_run.get("attacker_cost"),
        "harm": witness_run.get("harm"),
        "standing": "descriptive figure beside the witness",
        "priced_per": "failure witness run",
        "regime_classification_changed": False,
        "classification_before": witness_run.get(
            "regime_classification"),
        "classification_after": witness_run.get(
            "regime_classification"),
        "units": UNITS,
    }


def witness_carriage(witness_run, envelope_claim_names_witness=True):
    """The witness carriage this slice supplies for one run."""
    carriage = {
        "witness_run": witness_run.get("run_identifier"),
        "regime_classification": witness_run.get(
            "regime_classification"),
    }
    if envelope_claim_names_witness:
        carriage["attacker_cost_summary"] = attacker_cost_summary(
            witness_run)
    return carriage


def search_record_covers_hostile_kinds(record, family_record_kinds):
    """Check the hostile input family carriage of one record.

    Each kind stands with a magnitude or range fixed in the family
    record before runs. A kind run below its fixed magnitude does
    not count as run.
    """
    covered = {}
    runs = record.get("hostile_kind_runs", {})
    for kind in HOSTILE_INPUT_KINDS:
        fixed = (family_record_kinds or {}).get(kind)
        ran = runs.get(kind)
        if fixed is None or ran is None:
            covered[kind] = False
        else:
            covered[kind] = ran >= fixed
    return covered


class AttackerSeat:
    """The Attacker Seat: mechanism and ladder carriage."""

    def __init__(self, strategy_class=None, ladder_position=None,
                 catalogue_version_or_hash=None,
                 ladder_definition_pointer=None,
                 ladder_definition_version=None):
        self.strategy_class = strategy_class
        self.ladder_position = ladder_position
        self.catalogue_version_or_hash = catalogue_version_or_hash
        self.ladder_definition_pointer = ladder_definition_pointer
        self.ladder_definition_version = ladder_definition_version

    def run_record_carriage(self, strategies=None):
        return run_record_carriage(
            self.strategy_class, self.ladder_position,
            self.catalogue_version_or_hash,
            self.ladder_definition_pointer,
            self.ladder_definition_version, strategies=strategies)

    def run_search(self, points_tried, per_point_outcome,
                   bond_candidates, strategies=None, **kwargs):
        carriage = self.run_record_carriage(strategies=strategies)
        return run_search(carriage, points_tried, per_point_outcome,
                          bond_candidates, **kwargs)

    def search(self, *args, **kwargs):
        return self.run_search(*args, **kwargs)

    def bond_search(self, parameter_candidates,
                    griefing_evaluator=None):
        return bond_search(parameter_candidates, griefing_evaluator)

    def readout(self, search_record, **kwargs):
        return readout(search_record, **kwargs)

    def stopping_rule_state(self):
        return stopping_rule_state(self.ladder_position)

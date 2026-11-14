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
    "\u0430": "a", "\u0441": "c", "\u0435": "e", "\u043e": "o",
    "\u0440": "p", "\u0445": "x", "\u0443": "y", "\u0456": "i",
    "\u0458": "j", "\u0455": "s", "\u04bb": "h", "\u043a": "k",
    "\u043c": "m", "\u043d": "h", "\u0442": "t", "\u0432": "b",
    "\u03b1": "a", "\u03b2": "b", "\u03b5": "e", "\u03b9": "i",
    "\u03ba": "k", "\u03bc": "m", "\u03bf": "o", "\u03c1": "p",
    "\u03c4": "t", "\u03c7": "x", "\u03c5": "u", "\u03bd": "n",
    "\u03b3": "g", "\u03b4": "d", "\u03bb": "l", "\u03c3": "s",
    "\u03c9": "w", "\u03b6": "z", "\u03b8": "t", "\u03c6": "f",
    "\u044d": "e", "\u043b": "l", "\u03c8": "ps",
    "\u00e6": "ae", "\u0153": "oe", "\u00f8": "o", "\u0111": "d",
    "\u0142": "l", "\u00df": "ss", "\u00fe": "th", "\u00f0": "d",
    "\u0127": "h", "\u014b": "n", "\u0192": "f", "\u0131": "i",
    "\u0167": "t",
    "\u00c6": "ae", "\u0152": "oe", "\u00d8": "o", "\u0110": "d",
    "\u0141": "l", "\u1e9e": "ss", "\u00de": "th", "\u00d0": "d",
    "\u0126": "h", "\u014a": "n", "\u0191": "f", "\u0166": "t",
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
    "\u0431": "b", "\u0433": "g", "\u0434": "d", "\u0438": "i",
    "\u043f": "p",
    "\u0451": "e", "\u0452": "s", "\u0493": "h",
    "\u03c2": "s",
    "\u0585": "o", "\u0555": "o", "\u0578": "n", "\u0548": "n",
    "\u1d00": "a", "\u0299": "b", "\u1d04": "c", "\u1d05": "d",
    "\u1d07": "e", "\ua730": "f", "\u0262": "g", "\u029c": "h",
    "\u026a": "i", "\u1d0a": "j", "\u1d0b": "k", "\u029f": "l",
    "\u1d0d": "m", "\u0274": "n", "\u1d0f": "o", "\u1d18": "p",
    "\ua7af": "q", "\u0280": "r", "\ua731": "s", "\u1d1b": "t",
    "\u1d1c": "u", "\u1d20": "v", "\u1d21": "w", "\u028f": "y",
    "\u1d22": "z",
    "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l",
    "\u00a5": "y",
    "\u00a2": "c", "\u00a7": "s", "+": "t",
    "\u13d2": "r", "\u13ac": "e", "\u13aa": "a", "\u13de": "l",
    "\u13b7": "m", "\u13be": "o", "\u13c1": "n", "\u13ef": "y",
    "\uaba2": "r", "\uab7c": "e", "\uab7a": "a", "\uabae": "l",
    "\uab87": "m", "\uab8e": "o", "\uab91": "n", "\uabbf": "y",
    "\u2ca3": "r", "\u2c89": "e", "\u2c81": "a", "\u2c97": "l",
    "\u2c99": "m", "\u2c9f": "o", "\u2c9b": "n", "\u2ca9": "y",
}
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
    "\u0440": "r", "\u0445": "h", "\u0432": "v", "\u0441": "s",
    "\u043d": "n", "\u0443": "u",
    "\u03b7": "e", "\u03c0": "p", "\u03c7": "h", "\u03c1": "r",
    "\u03c9": "o",
}
_ALT_LETTER_MAP = dict(_WIDE_LETTER_MAP)
_ALT_LETTER_MAP.update(_TRANSLITERATION_OVERRIDES)
for _upper, _lower in list(_TRANSLITERATION_OVERRIDES.items()):
    _ALT_LETTER_MAP[_upper.upper()] = _lower

_DROPPED_INVISIBLE = frozenset(
    ["\u200b", "\u200c", "\u200d", "\ufeff", "\u00ad", "\u2060"])

_LEET_MAP = {
    "0": "o", "1": "i", "3": "e", "4": "a",
    "5": "s", "7": "t", "8": "b", "@": "a", "$": "s",
    "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l",
    "\u00a5": "y", "\u00a2": "c", "\u00a7": "s", "+": "t",
}


def _canonical_text(key, letter_map=None):
    mapping = _HOMOGLYPH_MAP if letter_map is None else letter_map
    decomposed = unicodedata.normalize("NFKD", str(key))
    chars = []
    for character in decomposed:
        if character in _DROPPED_INVISIBLE:
            continue
        if unicodedata.category(character).startswith("M"):
            continue
        chars.append(mapping.get(character, character))
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
    lowered = str(key).lower()
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
        )
    if id(value) in seen:
        raise NamedGeneratorFailure(
            "ground truth traversal found a cycle at " + (path or "root")
        )


AgentState = _mod01.AgentState
VouchEdge = _mod01.VouchEdge


def mod01_surface():
    """Return the MOD-01 module this generator depends on."""
    return _mod01


def mod01_type(name):
    """Return a type named on the MOD-01 surface, or None if absent."""
    return getattr(_mod01, name, None)


def make_archetype_record(archetype_id=None, behaviour=None,
                          parameter_rows=None, generator_signature=None,
                          ground_truth_label=None, farm_member=False):
    """Build one archetype record, the data a generator is driven by.

    Only archetype behaviour is stated in the record: the behaviour
    mapping, its parameter rows, and its generator signature. No rule
    state and no strategy stands in the record. The strategy class
    for a run is stated on the cast, never in an archetype record.
    """
    return {
        "archetype_id": archetype_id,
        "behaviour": dict(behaviour or {}),
        "parameter_rows": list(parameter_rows or ()),
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
    for record in records or ():
        identifier = record.get("archetype_id")
        if identifier is None:
            raise ValueError(
                "catalogue rejected: an archetype record carries no "
                "identifier"
            )
        if identifier in entries:
            raise ValueError(
                "catalogue rejected: a duplicate archetype identifier "
                "stands in the record set: " + str(identifier)
            )
        entries[identifier] = {
            "generator_signature": record.get("generator_signature"),
            "parameter_rows": list(record.get("parameter_rows") or ()),
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
    return all(identifier in entries for identifier in archetype_ids)


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
        return list(stream_state)
    if isinstance(stream_state, dict):
        if preferred_key is not None and isinstance(
                stream_state.get(preferred_key), (list, tuple)):
            return list(stream_state[preferred_key])
        if isinstance(stream_state.get("values"), (list, tuple)):
            return list(stream_state["values"])
        candidates = [
            (key, value) for key, value in stream_state.items()
            if isinstance(value, (list, tuple))
        ]
        if candidates:
            candidates.sort(key=lambda item: str(item[0]))
            return list(candidates[0][1])
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
            "count: " + repr(farm_size))
    return farm_size


def _records_by_id(archetype_records):
    by_id = {}
    for record in archetype_records or ():
        by_id[record.get("archetype_id")] = record
    return by_id


def build_cast(point, archetype_records, stream_state=None,
               strategy_class=None, initial_edges=None):
    """Build the cast for one run and deliver it before day one.

    The point names the population and the archetype mix. The mix
    counts must sum to the population, and every archetype in the mix
    must stand in the records supplied. The strategy class for a run is
    fixed in advance: a cast with no strategy class stated does not
    build. Cast order is a deterministic function of the stream state
    values handed in: where cast values stand supplied, one per agent,
    agents take their archetypes in the order those values state, ties
    broken by agent identifier.
    """
    if not strategy_class or not isinstance(strategy_class, str):
        raise ValueError("the strategy class for a run is fixed in "
                         "advance and must be stated before the run")
    if not isinstance(point, dict):
        raise ValueError("the point for a cast is not a record")
    population = point.get("population_size", point.get("population"))
    mix = point.get("archetype_mix") or {}
    if population is None:
        raise ValueError("the point states no population")
    if isinstance(population, bool) or not isinstance(
            population, int) or population < 0:
        raise NamedGeneratorFailure(
            "cast rejected: the population the point states is not "
            "a non negative whole count: " + repr(population))
    for mix_identifier, mix_count in mix.items():
        if isinstance(mix_count, bool) or not isinstance(
                mix_count, int) or mix_count < 0:
            raise NamedGeneratorFailure(
                "cast rejected: the mix count for "
                + str(mix_identifier) + " is not a non negative "
                "whole count: " + repr(mix_count))
    if sum(mix.values()) != population:
        raise ValueError("archetype mix counts do not sum to the "
                         "population the point names")
    by_id = _records_by_id(archetype_records)
    for identifier in mix:
        if identifier not in by_id:
            raise ValueError("archetype in the mix stands outside "
                             "the records supplied: " + str(identifier))
    agent_ids = ["agent-%04d" % index for index in range(population)]
    order = list(agent_ids)
    cast_values = _stream_values(stream_state, "cast")
    if cast_values:
        if len(cast_values) != population:
            raise ValueError("cast stream values do not cover the "
                             "population")
        order = [agent for _value, agent in sorted(
            zip(cast_values, agent_ids),
            key=lambda pair: (pair[0], pair[1]))]
    assignment = []
    for identifier, count in mix.items():
        assignment.extend([identifier] * count)
    farm_size = _guard_farm_size(point.get("farm_size"), "cast rejected")
    farm_members = []
    agents = []
    farm_of = {}
    for agent_id, archetype_id in zip(order, assignment):
        record = by_id[archetype_id]
        farm_id = None
        if record.get("farm_member") and farm_size:
            farm_members.append(agent_id)
            farm_id = "farm-%d" % ((len(farm_members) - 1) // farm_size)
        farm_of[agent_id] = farm_id
        agents.append({
            "agent_id": agent_id,
            "archetype_id": archetype_id,
            "ground_truth": record.get("ground_truth_label"),
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
        edge_source = point.get("initial_edges")
    for edge in edge_source or ():
        if isinstance(edge, dict):
            edges.append({
                "voucher": edge.get("voucher"),
                "vouchee": edge.get("vouchee"),
                "stake": edge.get("stake", 0),
            })
        elif isinstance(edge, (str, bytes)):
            raise NamedGeneratorFailure(
                "cast rejected: an initial edge stands as text, "
                "not as a voucher and vouchee pair: " + repr(edge))
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
                "and vouchee pair of size two: " + repr(edge))
    internal_counts = {}
    for farm in farms:
        internal_counts[farm["farm_id"]] = 0
    for edge in edges:
        first = farm_of.get(edge["voucher"])
        if first is not None and first == farm_of.get(edge["vouchee"]):
            internal_counts[first] += 1
    cast_record = {
        "delivery_point": "before day one",
        "point_id": point.get("point_id", point.get("point_identifier")),
        "strategy_class": strategy_class,
        "population": population,
        "archetype_counts": dict(mix),
        "cast": agents,
        "farms": farms,
        "initial_graph": {"edges": edges},
        "internal_edge_count_per_farm": internal_counts,
        "deliveries_after_day_one": (
            "behaviour through the behaviour streams only"),
    }
    if not farm_size and any(
            by_id[agent["archetype_id"]].get("farm_member")
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
        "agent_identifier": agent.get("agent_id"),
        "archetype_identifier": agent.get("archetype_id"),
        "membership_ground_truth": agent.get("ground_truth"),
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
        "voucher": edge.get("voucher"),
        "vouchee": edge.get("vouchee"),
        "stake": edge.get("stake"),
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


def construct_farm(member_ids, farm_size=None, edges=None):
    """Construct farms over a member set and count internal edges.

    Returns the farm identities with their members and the internal
    edge count per farm identity, the count the run record carries.
    With no edges stated, every internal count stands at zero.
    """
    members = list(member_ids or ())
    farm_size = _guard_farm_size(farm_size, "farm rejected")
    if not farm_size:
        farms = []
        farm_of = {member: None for member in members}
    else:
        grouped = {}
        farm_of = {}
        for index, member in enumerate(members):
            farm_id = "farm-%d" % (index // farm_size)
            grouped.setdefault(farm_id, []).append(member)
            farm_of[member] = farm_id
        farms = [
            {"farm_id": farm_id, "member_ids": list(grouped[farm_id])}
            for farm_id in sorted(grouped)
        ]
    counts = {farm["farm_id"]: 0 for farm in farms}
    for edge in edges or ():
        if isinstance(edge, dict):
            if dict.get(edge, "vouchee") is None:
                raise NamedGeneratorFailure(
                    "farm rejected: an edge carries no vouchee, "
                    "not as a voucher and vouchee pair: "
                    + repr(edge))
            first, second = edge.get("voucher"), edge.get("vouchee")
        elif isinstance(edge, (str, bytes)):
            raise NamedGeneratorFailure(
                "farm rejected: an edge stands as text, not as a "
                "voucher and vouchee pair: " + repr(edge))
        elif isinstance(edge, (list, tuple)) and len(edge) == 2:
            first, second = edge[0], edge[1]
        else:
            raise NamedGeneratorFailure(
                "farm rejected: an edge is not a voucher and "
                "vouchee pair of size two: " + repr(edge))
        farm_id = farm_of.get(first)
        if farm_id is not None and farm_id == farm_of.get(second):
            counts[farm_id] += 1
    return {
        "farms": farms,
        "internal_edge_count_per_farm_identity": counts,
    }


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
        "AN-1", point.get("anchor_set_description", "scenario setting"))
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
    record = archetype_record or {}
    behaviour = record.get("behaviour") or {}
    action = behaviour.get("action", "propose")
    if isinstance(stream_state, (int, float)):
        values = [stream_state]
    else:
        values = _stream_values(stream_state, "behaviour")
    proposals = []
    for value in values:
        proposals.append({
            "agent_id": agent_id,
            "archetype_id": record.get("archetype_id"),
            "action": action,
            "draw": value,
            "assumptions": dict(assumption_values or {}),
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
    """Iterate a list, tuple, set, or frozenset part through its
    base class iteration, never through a reading the part
    itself supplies, so a part whose own iteration yields
    nothing still stands read by the contents in its base
    class storage."""
    iter_by_base = {list: list.__iter__, tuple: tuple.__iter__,
                    set: set.__iter__, frozenset: frozenset.__iter__}
    for base, base_iter in iter_by_base.items():
        if isinstance(value, base):
            return base_iter(value)
    return iter(value)


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
    """
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        seen = _seen if _seen is not None else set()
        _traversal_guard(value, _depth, seen, _path)
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                return any(
                    key in RULE_STATE_FIELDS
                    or _value_carries_rule_state(
                        item, _depth + 1, seen, _path + "/" + str(key))
                    for key, item in dict.items(value)
                )
            return any(
                _value_carries_rule_state(
                    item, _depth + 1, seen,
                    _path + "[" + str(index) + "]")
                for index, item in enumerate(_base_iter(value))
            )
        finally:
            seen.discard(id(value))
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
    barred key nested inside a feature value, inside a rule record,
    or inside a container at any further depth still counts.
    """
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        seen = _seen if _seen is not None else set()
        _traversal_guard(value, _depth, seen, _path)
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                for key, item in dict.items(value):
                    if isinstance(
                            key, (dict, list, tuple, set, frozenset)):
                        if _value_carries_ground_truth(
                                key, _depth + 1, seen,
                                _path + "/key"):
                            return True
                    elif _is_barred_key(key):
                        return True
                    if _value_carries_ground_truth(
                            item, _depth + 1, seen,
                            _path + "/" + str(key)):
                        return True
                return False
            return any(
                _value_carries_ground_truth(
                    item, _depth + 1, seen, _path + "[" + str(index) + "]")
                for index, item in enumerate(_base_iter(value))
            )
        finally:
            seen.discard(id(value))
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
    """
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        seen = _seen if _seen is not None else set()
        _traversal_guard(value, _depth, seen, _path)
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                stripped = {}
                for key, item in dict.items(value):
                    if isinstance(
                            key, (dict, list, tuple, set, frozenset)):
                        new_key = _strip_ground_truth_value(
                            key, _depth + 1, seen, _path + "/key")
                    else:
                        if _is_barred_key(key):
                            continue
                        new_key = key
                    stripped[new_key] = _strip_ground_truth_value(
                        item, _depth + 1, seen,
                        _path + "/" + str(key))
                return stripped
            if isinstance(value, list):
                return [
                    _strip_ground_truth_value(
                        item, _depth + 1, seen, _path + "[" + str(index) + "]")
                    for index, item in enumerate(_base_iter(value))
                ]
            if isinstance(value, tuple):
                return tuple(
                    _strip_ground_truth_value(
                        item, _depth + 1, seen, _path + "[" + str(index) + "]")
                    for index, item in enumerate(_base_iter(value))
                )
            return value
        finally:
            seen.discard(id(value))
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
    no degree stated.
    """
    if isinstance(day, bool) or not isinstance(day, int):
        raise NamedGeneratorFailure(
            "cold society degree rejected: the stated day is not "
            "a whole count day in its stated form: " + repr(day))
    if int.__le__(int.__new__(int, day), COLD_SOCIETY_FIRST_DAYS):
        return 0
    for operand, naming in ((envelope, "envelope"),
                            (gate_passing_share, "gate passing share")):
        if operand is not None and (
                isinstance(operand, bool)
                or not isinstance(operand, (int, float))):
            raise NamedGeneratorFailure(
                "cold society degree rejected: the stated "
                + naming + " is not a number in its stated "
                "form: " + repr(operand))
    if envelope is None or gate_passing_share is None:
        return {
            "degree": None,
            "standing": "gated by the gate passing share",
            "provenance_label": COLD_SOCIETY_PROVENANCE,
        }
    plain_envelope = (
        float.__new__(float, envelope) if isinstance(envelope, float)
        else int.__new__(int, envelope))
    plain_share = (
        float.__new__(float, gate_passing_share)
        if isinstance(gate_passing_share, float)
        else int.__new__(int, gate_passing_share))
    if isinstance(plain_envelope, float) or isinstance(
            plain_share, float):
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
    if not strategy_class:
        raise ValueError("a new archetype enters only under the "
                         "fixed strategy class for a run")
    before = archetype_catalogue(records)
    after = archetype_catalogue(list(records or ()) + [new_record])
    added = new_record.get("archetype_id")
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
            "generator_signature": new_record.get("generator_signature"),
            "parameter_rows": list(
                new_record.get("parameter_rows") or ()),
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

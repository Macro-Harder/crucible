"""MOD-04 Tick Engine, DetectionInput projection, and view edges.

Slice S-09 in full, with the S-11 view edges this module owns. This
module carries the Contract A handover, the delivery points to the
rule cores and to the detection layer, the order of work inside one
simulated day, the DetectionInput projection from AgentState, and
the ViewRecord acts of slice S-11: selecting the records a view
contains, writing the ViewRecord, and delivering the view under
Contract K. Executable runs stand gated on DQ7-02: every barred
executable path in this module refuses by raising GatedRun, whose
message carries the recorded gated failure name DERIVATION-GATED
and names the gate DQ7-02, and no such path executes in part. The
tracer composition that retains and reads back one form only
RunRecord stands at the integration surface of slice S-16, in
mod16; this module holds no module level import of MOD-10, and
it delegates to MOD-10 at body level in two places only,
release_view calling the MOD-10 view leak check runner as the
release gate and write_checkpoint retaining the checkpoint pair
through the MOD-10 paired store.
"""
import copy
import unicodedata

GATE_EXECUTABLE_RUNS = "DQ7-02"

BARRED_PROJECTION_KEYS = frozenset([
    "ground_truth", "ground_truth_field", "membership",
    "honest_membership", "farm_membership", "is_honest", "is_farm",
    "canary", "canary_value", "membership_value", "sleeper",
    "ground_truth_label", "label",
])

PROJECTION_KEYS = ("agent_identifier", "day", "feature_values", "rule_records")

CANARY_VALUE = "F09-CANARY-MEMBERSHIP-VALUE"


class NamedFailure(Exception):
    """A failure stated by name, never a partial record as complete."""


class AlterationBarred(NamedFailure):
    pass


GATED_FAILURE_NAME = "DERIVATION-GATED"


class GatedRun(NamedFailure):
    """The one gated refusal form of this module for gate DQ7-02.

    Every executable path the gate bars raises this exception. Its
    message carries the recorded gated failure name and names the
    gate, so a scan for gated behaviour finds one form here and the
    matching refusal record form in MOD-02.
    """

    failure = GATED_FAILURE_NAME
    gate = GATE_EXECUTABLE_RUNS


def _gated_message(act):
    return (
        GATED_FAILURE_NAME + ": " + act + " stands gated on "
        + GATE_EXECUTABLE_RUNS
        + ". No adoption record stands for this gate, so nothing was "
        "started or drawn. Nothing stands for the operator to do; "
        "the block sits with a decision elsewhere."
    )


def _freeze(value):
    return copy.deepcopy(value)


def _guarded_copy(value, _memo=None):
    """Copy a value through base class readings only, the guarded
    copy form the sister copy acts state. Dict parts stand read
    through the base dict items reading, and list, tuple, set,
    and frozenset parts through their base iteration readings,
    built as plain containers of their kind, so no copy protocol
    a part supplies is ever invoked and a part supplying a lying
    deepcopy protocol cannot materialise as another value inside
    the copy. A part in no container form stands copied as
    itself."""
    if _memo is None:
        _memo = {}
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied[_guarded_copy(key, _memo)] = _guarded_copy(item, _memo)
        return copied
    if isinstance(value, list):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = []
        _memo[id(value)] = copied
        copied.extend(
            _guarded_copy(item, _memo) for item in list.__iter__(value))
        return copied
    if isinstance(value, tuple):
        return tuple(
            _guarded_copy(item, _memo) for item in tuple.__iter__(value))
    if isinstance(value, frozenset):
        return frozenset(
            _guarded_copy(item, _memo) for item in frozenset.__iter__(value))
    if isinstance(value, set):
        return set(
            _guarded_copy(item, _memo) for item in set.__iter__(value))
    return value


class ContractAHandover:
    """One point, one assumption record, one seed input set, and one
    family identifier for one run, in interface form. The engine may
    not alter any handed value. Values are stored as deep copies and
    handed back as deep copies, so no caller side mutation reaches
    the stored handover, and any engine side attempt to change a
    stored value is checked by verify_intact."""

    __slots__ = ("_point", "_assumption_record", "_seed_input_set", "_family_id", "_sealed")

    def __init__(self, point, assumption_record, seed_input_set, family_id):
        object.__setattr__(self, "_point", _freeze(point))
        object.__setattr__(self, "_assumption_record", _freeze(assumption_record))
        object.__setattr__(self, "_seed_input_set", _freeze(seed_input_set))
        object.__setattr__(self, "_family_id", _freeze(family_id))
        object.__setattr__(self, "_sealed", True)

    def __setattr__(self, name, value):
        raise AlterationBarred("Contract A handed values may not be altered: " + str(name))

    @property
    def point(self):
        return _freeze(self._point)

    @property
    def assumption_record(self):
        return _freeze(self._assumption_record)

    @property
    def seed_input_set(self):
        return _freeze(self._seed_input_set)

    @property
    def family_id(self):
        return _freeze(self._family_id)

    def verify_intact(self, point, assumption_record, seed_input_set, family_id):
        ok = (
            point == self._point
            and assumption_record == self._assumption_record
            and seed_input_set == self._seed_input_set
            and family_id == self._family_id
        )
        if not ok:
            raise AlterationBarred(
                "silent correction inside the Engine: a handed value differs from the Contract A handover"
            )
        return True

    def as_dict(self):
        return {
            "point": self.point,
            "assumption_record": self.assumption_record,
            "seed_input_set": self.seed_input_set,
            "family_id": self.family_id,
            "form": "interface",
            "alteration_bar": "engine may not alter point, assumptions, seeds, or family identifier",
        }


class DeliveryPoint:
    """A named delivery point in interface form only. It records
    interface deliveries and delivers nothing in running form."""

    def __init__(self, name, destination):
        self.name = name
        self.destination = destination
        self.deliveries = []
        self.form = "interface"

    def record_interface_delivery(self, payload_description):
        entry = {
            "delivery_point": self.name,
            "destination": self.destination,
            "form": "interface",
            "payload": _freeze(payload_description),
            "running_delivery": False,
        }
        self.deliveries.append(entry)
        return entry

    def deliver_running(self, payload):
        raise GatedRun(_gated_message("running delivery"))


class RuleCoreDeliveryPoint(DeliveryPoint):
    def __init__(self):
        super().__init__("rule_core_delivery", "rule_cores")


class DetectionLayerDeliveryPoint(DeliveryPoint):
    def __init__(self):
        super().__init__("detection_layer_delivery", "detection_layer")


def _state_field(state, names, default=None):
    if isinstance(state, dict):
        for name in names:
            if name in state:
                return state[name]
        return default
    for name in names:
        if hasattr(state, name):
            return getattr(state, name)
    return default


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
    "\u00e6": "ae", "\u0153": "oe", "\u00f8": "o", "\u0111": "d",
    "\u0142": "l", "\u00df": "ss", "\u00fe": "th", "\u00f0": "d",
    "\u0127": "h", "\u014b": "n", "\u0192": "f", "\u0131": "i",
    "\u0167": "t",
    "\u00c6": "ae", "\u0152": "oe", "\u00d8": "o", "\u0110": "d",
    "\u0141": "l", "\u1e9e": "ss", "\u00de": "th", "\u00d0": "d",
    "\u0126": "h", "\u014a": "n", "\u0191": "f", "\u0166": "t",
    "\u0431": "b", "\u0433": "g", "\u0434": "d", "\u0438": "i",
    "\u043f": "p", "\u03b7": "e", "\u03c0": "p", "\u03c2": "s",
    "\u0585": "o", "\u0555": "o", "\u0578": "n", "\u0548": "n",
    "\u1d00": "a", "\u0299": "b", "\u1d04": "c", "\u1d05": "d",
    "\u1d07": "e", "\ua730": "f", "\u0262": "g", "\u029c": "h",
    "\u026a": "i", "\u1d0a": "j", "\u1d0b": "k", "\u029f": "l",
    "\u1d0d": "m", "\u0274": "n", "\u1d0f": "o", "\u1d18": "p",
    "\ua7af": "q", "\u0280": "r", "\ua731": "s", "\u1d1b": "t",
    "\u1d1c": "u", "\u1d20": "v", "\u1d21": "w", "\u028f": "y",
    "\u1d22": "z",
    "\u1d31": "e", "\u1d38": "l", "\u1d3c": "o", "\u1d40": "t",
    "\u0452": "s", "\u0493": "h",
    "\u13d2": "r", "\uaba2": "r", "\u13ac": "e", "\uab7c": "e",
    "\u13aa": "a", "\uab7a": "a", "\u13de": "l", "\uabae": "l",
    "\u13b7": "m", "\uab87": "m", "\u13be": "o", "\uab8e": "o",
    "\u13c1": "n", "\uab91": "n", "\u13ef": "y", "\uabbf": "y",
    "\u2ca3": "r", "\u2c89": "e", "\u2c81": "a", "\u2c97": "l",
    "\u2c99": "m", "\u2c9f": "o", "\u2c9b": "n", "\u2ca9": "y",
    "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l", "\u00a5": "y",
    "\u00a2": "c", "\u00a7": "s", "+": "t",
}
for _upper, _lower in list(_HOMOGLYPH_MAP.items()):
    _HOMOGLYPH_MAP[_upper.upper()] = _lower

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
    "\u0455": "s", "\u04bb": "h", "\u0456": "i",
    "\u0452": "s", "\u0493": "h",
    "\u13d2": "r", "\uaba2": "r", "\u13ac": "e", "\uab7c": "e",
    "\u13aa": "a", "\uab7a": "a", "\u13de": "l", "\uabae": "l",
    "\u13b7": "m", "\uab87": "m", "\u13be": "o", "\uab8e": "o",
    "\u13c1": "n", "\uab91": "n", "\u13ef": "y", "\uabbf": "y",
    "\u2ca3": "r", "\u2c89": "e", "\u2c81": "a", "\u2c97": "l",
    "\u2c99": "m", "\u2c9f": "o", "\u2c9b": "n", "\u2ca9": "y",
    "\u03b1": "a", "\u03b2": "b", "\u03b3": "g", "\u03b4": "d",
    "\u03b5": "e", "\u03b6": "z", "\u03b7": "e", "\u03b8": "th",
    "\u03b9": "i", "\u03ba": "k", "\u03bb": "l", "\u03bc": "m",
    "\u03bd": "n", "\u03bf": "o", "\u03c0": "p", "\u03c1": "r",
    "\u03c2": "s", "\u03c3": "s", "\u03c4": "t", "\u03c5": "u",
    "\u03c6": "ph", "\u03c7": "h", "\u03c8": "ps", "\u03c9": "o",
    "\u00e6": "ae", "\u0153": "oe", "\u00f8": "o", "\u0111": "d",
    "\u0142": "l", "\u00df": "ss", "\u00fe": "th", "\u00f0": "d",
    "\u0127": "h", "\u014b": "n", "\u0192": "f", "\u0131": "i",
    "\u0167": "t",
    "\u1d00": "a", "\u0299": "b", "\u1d04": "c", "\u1d05": "d",
    "\u1d07": "e", "\ua730": "f", "\u0262": "g", "\u029c": "h",
    "\u026a": "i", "\u1d0a": "j", "\u1d0b": "k", "\u029f": "l",
    "\u1d0d": "m", "\u0274": "n", "\u1d0f": "o", "\u1d18": "p",
    "\ua7af": "q", "\u0280": "r", "\ua731": "s", "\u1d1b": "t",
    "\u1d1c": "u", "\u1d20": "v", "\u1d21": "w", "\u028f": "y",
    "\u1d22": "z",
    "\u1d31": "e", "\u1d38": "l", "\u1d3c": "o", "\u1d40": "t",
    "\u0585": "o", "\u0555": "o", "\u0578": "n", "\u0548": "n",
    "@": "a", "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l",
    "\u00a5": "y", "$": "s", "\u00a2": "c", "\u00a7": "s", "+": "t",
}
for _upper, _lower in list(_TRANSLITERATION_MAP.items()):
    _TRANSLITERATION_MAP[_upper.upper()] = _lower

_LEET_MAP = {
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s",
    "\u20ac": "e", "\u00a3": "l", "!": "l", "|": "l", "\u00a5": "y",
}


def _base_entries(value):
    """The (index, item) entries of a container, read through the
    base class of its kind, never through an iteration reading the
    value itself supplies. A list or tuple subclass whose own
    iteration yields nothing therefore hides nothing it holds in
    base class storage, and a set or frozenset reads the same way."""
    if isinstance(value, list):
        return [
            (index, list.__getitem__(value, index))
            for index in range(list.__len__(value))
        ]
    if isinstance(value, tuple):
        return [
            (index, tuple.__getitem__(value, index))
            for index in range(tuple.__len__(value))
        ]
    if isinstance(value, frozenset):
        return list(enumerate(frozenset.__iter__(value)))
    if isinstance(value, set):
        return list(enumerate(set.__iter__(value)))
    return list(enumerate(value))


def _folded_readings(key):
    """The folded readings of one key, in the canonicalised form
    the Round 5 register states for the barred surfaces. The base
    reading lowercases the key, applies compatibility decomposition
    with combining marks dropped, maps non Latin homoglyph letters
    to the Latin letters they stand for, and drops every character
    that is not a letter or a digit, so a separator, a zero width
    character, or a soft hyphen standing inside a word holds the
    word apart no longer. Two further readings stand beside it: one
    with digit and symbol substitutions read as the letters they
    stand for, and one with digits dropped, so a digit standing
    inside a word as a split reads as the word it splits."""
    decomposed = unicodedata.normalize(
        "NFKD", str(key).lower()).lower()
    characters = [
        character for character in decomposed
        if not unicodedata.category(character).startswith("M")
    ]
    readings = []

    def _add_readings(base):
        plain = "".join(
            character for character in base if character.isalnum())
        leet_applied_first = "".join(
            character for character in "".join(
                _LEET_MAP.get(character, character) for character in base)
            if character.isalnum())
        leet_one_as_i = "".join(
            character for character in "".join(
                "i" if character == "1"
                else _LEET_MAP.get(character, character)
                for character in base)
            if character.isalnum())
        for reading in (
            plain,
            leet_applied_first,
            leet_one_as_i,
            "".join(character for character in plain
                    if not character.isdigit()),
        ):
            if reading and reading not in readings:
                readings.append(reading)

    for letter_map in (_HOMOGLYPH_MAP, _TRANSLITERATION_MAP):
        _add_readings("".join(
            letter_map.get(character, character)
            for character in characters
        ))
        _add_readings("".join(
            letter_map.get(character, character)
            for character in str(key).lower()
        ))
    # Position by position combination of the two maps, in the
    # form the MOD-10 fold states: each character contributes the
    # readings both maps record for it, so a word needing the
    # transliteration reading at one position and the homoglyph
    # reading at another stands read as the word it spells. Where
    # the combination count would grow past the stated cap, the
    # combined readings stand abandoned and the two whole map
    # readings above stand as the readings of the key.
    # The combination and its count stand built over the original
    # characters of the key, before decomposition. Each original
    # character contributes every distinct reading recorded for
    # it: the reading of its decomposed base under each map, the
    # reading each map records for the character itself where one
    # stands recorded, and, for Cyrillic short i, both of its
    # recorded readings, y and i, since decomposition alone would
    # reduce that letter to its i reading and lose the y reading
    # its transliteration records. The bound counts the distinct
    # combined texts built on that per character option basis.
    texts = {""}
    combined = True
    for character in str(key).lower():
        base_characters = [
            part for part in unicodedata.normalize("NFKD", character)
            if not unicodedata.category(part).startswith("M")
        ]
        options = set()
        for letter_map in (_HOMOGLYPH_MAP, _TRANSLITERATION_MAP):
            options.add("".join(
                letter_map.get(part, part) for part in base_characters
            ))
            if character in letter_map:
                options.add(letter_map[character])
        if character == "\u0439":
            options.update(("y", "i"))
        expanded = {
            prefix + option
            for prefix in texts
            for option in options
        }
        if len(expanded) > 4096:
            combined = False
            break
        texts = expanded
    if combined:
        for base in texts:
            _add_readings(base)
    return tuple(readings)


_BARRED_FOLDED_EXACT = frozenset(
    reading
    for name in BARRED_PROJECTION_KEYS
    for reading in _folded_readings(name)
)
_BARRED_FOLDED_PARTS = ("membership", "groundtruth", "canary")


def _is_barred_key(key):
    lowered = str(key).lower()
    if (
        lowered in BARRED_PROJECTION_KEYS
        or any(part in lowered for part in _BARRED_KEY_PARTS)
    ):
        return True
    for reading in _folded_readings(key):
        if reading in _BARRED_FOLDED_EXACT:
            return True
        if any(part in reading for part in _BARRED_FOLDED_PARTS):
            return True
    return False


CLEANING_DEPTH_BOUND = 100

VALUE_APPEARS_DEPTH_BOUND = 100


def _clean_leaf_copy(value):
    """Copy one leaf part of a projection through no protocol the
    part itself supplies. A leaf part stands copied as itself, so
    a part carrying a lying deepcopy protocol cannot materialise
    as another value inside the delivered projection."""
    return value


def _clean_value(value, _depth=0, _seen=None, _path=""):
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > CLEANING_DEPTH_BOUND:
            raise NamedFailure(
                "projection cleaning bound reached at " + (_path or "root")
                + ": the value stands deeper than the stated bound of "
                + str(CLEANING_DEPTH_BOUND)
            )
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            raise NamedFailure(
                "projection cleaning found a cycle at " + (_path or "root")
            )
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                return {
                    _clean_value(
                        key, _depth + 1, seen, _path + "/" + str(key)):
                    _clean_value(item, _depth + 1, seen, _path + "/" + str(key))
                    for key, item in dict.items(value)
                    if not _is_barred_key(key)
                }
            if isinstance(value, list):
                return [
                    _clean_value(item, _depth + 1, seen, _path + "[" + str(index) + "]")
                    for index, item in _base_entries(value)
                ]
            if isinstance(value, tuple):
                return tuple(
                    _clean_value(item, _depth + 1, seen, _path + "[" + str(index) + "]")
                    for index, item in _base_entries(value)
                )
            if isinstance(value, set):
                return set(
                    _clean_value(item, _depth + 1, seen, _path + "[" + str(index) + "]")
                    for index, item in _base_entries(value)
                )
            return frozenset(
                _clean_value(item, _depth + 1, seen, _path + "[" + str(index) + "]")
                for index, item in _base_entries(value)
            )
        finally:
            seen.discard(id(value))
    return _clean_leaf_copy(value)


def _clean_feature_values(raw):
    cleaned = {}
    if isinstance(raw, dict):
        for key, value in dict.items(raw):
            if _is_barred_key(key):
                continue
            cleaned[_clean_value(key, 1, None, "/" + str(key))] = (
                _clean_value(value, 1, None, "/" + str(key)))
    return cleaned


def _clean_rule_records(raw):
    cleaned = []
    if isinstance(raw, (list, tuple)):
        for index, item in _base_entries(raw):
            cleaned.append(_clean_value(item))
    return cleaned


def project_detection_input(state):
    """Project AgentState to DetectionInput. The result carries the
    agent identifier, the day, the feature values, and the records
    the rules give the detection layer, and nothing else. It carries
    no ground truth field and no field derived from membership."""
    agent_id = _state_field(state, ["agent_identifier", "agent_id", "identifier"])
    day = _state_field(state, ["day", "simulated_day"])
    if agent_id is None or day is None:
        absent = []
        if agent_id is None:
            absent.append("agent identifier")
        if day is None:
            absent.append("day")
        raise NamedFailure(
            "projection requires an agent state carrying an agent identifier and a day: absent "
            + " and ".join(absent)
        )
    features = _state_field(state, ["feature_values", "features"], {})
    rule_records = _state_field(state, ["rule_records", "detection_records"], [])
    if not isinstance(features, dict):
        raise NamedFailure(
            "projection refused in named form: feature_values stands "
            "in a non record form and no projection stands written "
            "from it: " + type(features).__name__
        )
    if not isinstance(rule_records, list):
        raise NamedFailure(
            "projection refused in named form: rule_records stands "
            "in a non list form and no projection stands written "
            "from it: " + type(rule_records).__name__
        )
    return {
        "agent_identifier": agent_id,
        "day": day,
        "feature_values": _clean_feature_values(features),
        "rule_records": _clean_rule_records(rule_records),
    }


def _value_appears(value, node, _seen=None, _depth=0):
    if isinstance(node, (dict, list, tuple, set, frozenset)):
        if _depth > VALUE_APPEARS_DEPTH_BOUND:
            raise NamedFailure(
                "canary presence read bound reached: the value stands "
                "deeper than the stated bound of "
                + str(VALUE_APPEARS_DEPTH_BOUND)
            )
        seen = _seen if _seen is not None else set()
        if id(node) in seen:
            return False
        seen.add(id(node))
    if node == value:
        return True
    if isinstance(node, dict):
        return any(
            _value_appears(value, v, _seen, _depth + 1)
            for v in dict.values(node)
        ) or any(
            _value_appears(value, k, _seen, _depth + 1)
            for k in dict.keys(node)
        )
    if isinstance(node, (list, tuple, set, frozenset)):
        return any(
            _value_appears(value, item, _seen, _depth + 1)
            for index, item in _base_entries(node)
        )
    if isinstance(node, str) and isinstance(value, str):
        return value in node
    return False


def exercise_f09_canary(canary_value=CANARY_VALUE):
    """Fixture F-09 canary exercise, in code form. Places a canary
    membership value in an AgentState, runs the projection, and
    returns whether the canary appears in any projected record.
    The correct result is False: the canary must not appear."""
    state = {
        "agent_identifier": "agent-canary-1",
        "day": 1,
        "simulated_day": 1,
        "feature_values": {
            "activity": 1,
            "nested": {"membership": canary_value},
        },
        "rule_records": [
            {"kind": "daily_record", "detail": {"ground_truth": canary_value}},
        ],
        "membership": canary_value,
        "ground_truth": canary_value,
    }
    projected = project_detection_input(state)
    return _value_appears(canary_value, projected)


def canary_appears_in_projection(canary_value=CANARY_VALUE):
    return exercise_f09_canary(canary_value)


class TickEngine:
    """The Tick Engine interface. In the tracer cut it holds the
    Contract A handover, owns the two delivery points in interface
    form, and owns the projection. It is the sole writer of
    simulation state in interface form: a write attempted through
    any other writer name is rejected."""

    def __init__(self, handover=None):
        self.handover = handover
        self.rule_core_delivery = RuleCoreDeliveryPoint()
        self.detection_delivery = DetectionLayerDeliveryPoint()
        self.state_writes = []

    def write_simulation_state(self, writer, change):
        if writer is not self:
            raise NamedFailure(
                "direct state write from a second component is rejected: "
                "the write path requires the engine instance itself, not a name"
            )
        self.state_writes.append(_freeze(change))
        return True

    def tick(self, *args, **kwargs):
        return self.run(*args, **kwargs)

    def run(self, *args, **kwargs):
        raise GatedRun(_gated_message("executable runs"))


def run(*args, **kwargs):
    return TickEngine().run(*args, **kwargs)


def tick(*args, **kwargs):
    return TickEngine().tick(*args, **kwargs)


def build_tracer_run_record():
    """Assemble one RunRecord in form only, one family, one point,
    one run class, through the S-09 interfaces, with its deliveries
    recorded as interface deliveries."""
    handover = ContractAHandover(
        point={"point_id": "tracer-point-1"},
        assumption_record={"assumption_record_id": "tracer-assumptions-1"},
        seed_input_set={"seed_inputs": ["tracer-seed-input-1"]},
        family_id="tracer-family-1",
    )
    engine = TickEngine(handover)
    state = {
        "agent_identifier": "agent-tracer-1",
        "day": 1,
        "feature_values": {"activity": 1},
        "rule_records": [{"kind": "daily_record"}],
        "membership": CANARY_VALUE,
    }
    projected = project_detection_input(state)
    d1 = engine.rule_core_delivery.record_interface_delivery(
        {"kind": "event", "form": "interface"}
    )
    d2 = engine.detection_delivery.record_interface_delivery(
        {"kind": "DetectionInput", "form": "interface", "record": projected}
    )
    record = {
        "run_id": "tracer-run-1",
        "run_identifier": "tracer-run-1",
        "family_id": "tracer-family-1",
        "point": handover.point,
        "run_class": "screening",
        "form": "form_only",
        "reportable": False,
        "gate": GATE_EXECUTABLE_RUNS,
        "groups": {
            "assumption_record": handover.assumption_record,
            "identity_and_design": {
                "family_id": "tracer-family-1",
                "point": handover.point,
                "run_class": "screening",
            },
            "interpretation_choices": {},
            "joined_done_test": {},
            "outcome_and_retention": {"deliveries": [d1, d2]},
            "reserved_matter": {},
            "variant_stamp": {},
        },
        "deliveries": [d1, d2],
        "handover": handover.as_dict(),
    }
    return record, projected


def run_tracer_cut():
    """Tracer entry point, kept at this name by the suite pin in
    test_tg_09_3.py, which calls this function on this module. The
    composition itself stands at the integration surface of slice
    S-16, in mod16.run_tracer_cut: the engine delivers the record
    in form only, and the integration surface composes it with the
    MOD-10 retention and reading path. This function imports
    MOD-16 only; the module delegates to MOD-10 at body level in
    release_view and in write_checkpoint, as the head statement
    states."""
    from crucible import mod16

    return mod16.run_tracer_cut()


# ---------------------------------------------------------------------------
# S-09 in full: scheduling order, event sequence, delivery completeness
# ---------------------------------------------------------------------------

PROTOTYPE_ORDER = "prototype"
EVENT_KINDS = (
    "work_submission", "work_acceptance", "vouch_creation",
    "vouch_revocation", "challenge_opening", "challenge_response",
    "escrow_opening", "escrow_deposit", "escrow_release_request",
    "escrow_slash_request", "escrow_pause", "escrow_claim",
    "gossip_message", "trust_query", "detection_delivery",
    "day_close", "epoch_close",
)
PROCESSING_TYPES = (
    "gossip intake", "trust evaluation", "pairwise collusion evaluation",
)


def scheduling_order_record(family_id, order_identifier):
    """The scheduling order carriage of one family: one fixed order
    per family, stated in the family record the engine reads, never
    chosen inside engine code."""
    return {
        "family_id": family_id,
        "scheduling_order_identifier": order_identifier,
        "fixed_per_family": True,
        "stated_in": "family record",
    }


def run_record_with_order(run_record, order_identifier):
    """Return a copy of a run record carrying the scheduling order
    identifier the run used, as every run record must."""
    record = _freeze(run_record)
    record["scheduling_order_identifier"] = order_identifier
    return record


def validate_run_scheduling_order(record):
    """Return True only where a run record may stand on its order.

    Every run record states the order it used. A headline run whose
    scheduling order identifier is absent, or reads prototype,
    fails, per operation C-14 and open point OP-08.
    """
    if not isinstance(record, dict):
        return False
    order = record.get("scheduling_order_identifier")
    if not order:
        return False
    if record.get("run_class") == "headline" and order == PROTOTYPE_ORDER:
        return False
    return True


def headline_order_stands(record):
    """Return True only where a headline run order stands stated
    and is not a prototype order."""
    if not isinstance(record, dict):
        return False
    if record.get("run_class") != "headline":
        return False
    order = record.get("scheduling_order_identifier")
    return bool(order) and order != PROTOTYPE_ORDER


def measure_order_sensitivity(states_under_order_a, states_under_order_b):
    """The reverse order sensitivity check in family definition
    form: it measures a divergence between end of day states under
    two stated orders and states the size at which the order must
    be fixed. It fixes no order itself."""
    divergence = 0
    for key in set(states_under_order_a) | set(states_under_order_b):
        if states_under_order_a.get(key) != states_under_order_b.get(key):
            divergence += 1
    return {
        "divergence": divergence,
        "states_differ": divergence > 0,
        "order_must_be_fixed_at_divergence": 1,
        "order_fixed_by_this_check": False,
        "reportable_as": "order effect",
    }


def apply_event_to_state(state, event, engine=None):
    """Apply one event to simulation state. The engine is the sole
    writer: the change is written through write_simulation_state by
    the engine instance handed in, then the event feature updates
    land. With no engine instance handed in this act stands refused:
    it is not a second open write path."""
    if engine is None:
        raise NamedFailure(
            "applying an event to simulation state requires the TickEngine instance that owns the write"
        )
    engine.write_simulation_state(engine, {"event": _freeze(event)})
    updated = _freeze(state) if isinstance(state, dict) else {}
    updates = event.get("feature_updates") if isinstance(event, dict) else None
    if isinstance(updates, dict):
        features = dict(updated.get("feature_values") or {})
        features.update(_freeze(updates))
        updated["feature_values"] = features
    return updated


def process_day_events(state, events):
    """The sequence inside the tick, per event: first apply the
    event to simulation state through the rule core delivery point,
    then project the DetectionInput record from the state as it
    then stands, then deliver that record to the detection layer.
    Deliveries stand in interface form while the gate stands, and
    each projection carries the state after its own event and
    before any later event."""
    engine = TickEngine()
    current = _freeze(state) if isinstance(state, dict) else {}
    projections = []
    for event in events:
        current = apply_event_to_state(current, event, engine=engine)
        engine.rule_core_delivery.record_interface_delivery(
            {"kind": "event", "form": "interface", "event": _freeze(event)}
        )
        projected = project_detection_input(current)
        engine.detection_delivery.record_interface_delivery(
            {"kind": "DetectionInput", "form": "interface", "record": projected}
        )
        projections.append(projected)
    return {
        "state": current,
        "projections": projections,
        "rule_core_deliveries": engine.rule_core_delivery.deliveries,
        "detection_deliveries": engine.detection_delivery.deliveries,
        "sequence": ["apply", "project", "deliver"],
    }


def delivery_completeness(events, deliveries):
    """Return True only where every generated event in the day
    stands delivered. Processing types are not generated events
    and are never counted as events."""
    delivered_kinds = [
        entry.get("event", {}).get("kind")
        for entry in deliveries
        if isinstance(entry, dict) and isinstance(entry.get("event"), dict)
    ]
    expected = [event.get("kind") for event in events]
    return sorted(map(str, delivered_kinds)) == sorted(map(str, expected))


def is_processing_type(name):
    """Return True where a name is a processing type, not one of
    the generated event kinds."""
    return name in PROCESSING_TYPES


def projection_passed_for_run(run_record):
    """Return True only where the run record states its projection
    passed the F-09 canary test. A run whose projection has not
    passed is not reportable."""
    if not isinstance(run_record, dict):
        return False
    return run_record.get("projection_canary_passed") is True


def run_is_reportable(run_record):
    """A run is reportable only where its projection passed the
    canary test and its scheduling order stands for its class."""
    return (
        projection_passed_for_run(run_record)
        and validate_run_scheduling_order(run_record)
        and run_record.get("reportable") is not False
        and run_record.get("form") != "form_only"
    )


# ---------------------------------------------------------------------------
# S-11 view edges owned by MOD-04: selection, writing, delivery
# ---------------------------------------------------------------------------

COMPLETENESS_STATES = ("complete", "stale", "partial", "partitioned")
VIEW_CLOSED_FIELDS = (
    "run_identifier", "viewer_identifier", "simulated_day",
    "scheduling_position_identifier", "rule_version_set", "view_contents",
    "reputation_and_band_values", "graph_position_as_seen",
    "first_seen_day_per_record", "delay_applied_per_record",
    "completeness_state", "building_component", "delivering_contract",
    "selection_rule_version",
)
VIEW_EXCLUDED_CONTENT = (
    "ground truth field", "membership field",
    "field derived from membership", "record of another viewer",
)


VIEW_COPY_DEPTH_BOUND = 100


def _view_copy_guard(value, _depth=0, _seen=None, _path=""):
    """Walk a value the view select and build acts are about to
    copy, under the same depth bound and named failure form as
    the TA-03 cures: a value standing deeper than the bound, or
    carrying a cycle, raises NamedFailure naming the bound or
    the cycle at its path, and no bare RecursionError escapes
    the copy. A value shared from two places on different paths
    carries no cycle and stands admitted."""
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > VIEW_COPY_DEPTH_BOUND:
            raise NamedFailure(
                "view record copy bound reached at " + (_path or "root")
                + ": the value stands deeper than the stated bound of "
                + str(VIEW_COPY_DEPTH_BOUND)
            )
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            raise NamedFailure(
                "view record copy found a cycle at " + (_path or "root")
            )
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                for key, item in dict.items(value):
                    _view_copy_guard(
                        key, _depth + 1, seen, _path + "/" + str(key))
                    _view_copy_guard(
                        item, _depth + 1, seen, _path + "/" + str(key))
            else:
                for index, item in _base_entries(value):
                    _view_copy_guard(
                        item, _depth + 1, seen,
                        _path + "[" + str(index) + "]")
        finally:
            seen.discard(id(value))


def select_view_records(retained_records, viewer_id, as_of_day, delay=0,
                        as_of_position=None):
    """Select the records one viewer view contains. A record stands
    admitted only where it states a viewer match, under either
    viewer field name in use, and a stated day: an unscoped record
    and an undated record stand admitted to no view. Where an as of
    position stands supplied, the ruling comparison applies on
    first seen day and arising position: a record first seen before
    the view day stands admitted, and a record first seen on the
    view day stands admitted only where its arising position is at
    or before the as of position."""
    def _whole(value):
        return isinstance(value, int) and not isinstance(value, bool)

    def _viewer_matches(viewer, wanted):
        if isinstance(viewer, str):
            result = str.__eq__(viewer, wanted)
            return result if result is not NotImplemented else False
        if isinstance(wanted, str):
            return False
        return viewer == wanted

    def _base_add(first, second):
        result = int.__add__(first, second)
        return None if result is NotImplemented else result

    def _base_order(first, second, operation):
        result = operation(first, second)
        return result if result is not NotImplemented else False

    if not _whole(as_of_day) or not _whole(delay):
        return []
    if as_of_position is not None and not _whole(as_of_position):
        return []
    view_day = as_of_day
    delay_days = delay
    selected = []
    handed = retained_records or ()
    for index, record in _base_entries(handed):
        if not isinstance(record, dict):
            continue
        viewer = dict.get(record, "viewer_id")
        if viewer is None:
            viewer = dict.get(record, "viewer_identifier")
        if not _viewer_matches(viewer, viewer_id):
            continue
        first_seen = dict.get(record, "first_seen_day")
        if first_seen is None:
            first_seen = dict.get(record, "day")
        if first_seen is None:
            continue
        if not _whole(first_seen):
            continue
        first_seen_day = first_seen
        effective_day = _base_add(first_seen_day, delay_days)
        if effective_day is None:
            continue
        if _base_order(effective_day, view_day, int.__gt__):
            continue
        if as_of_position is not None:
            if (
                _base_order(effective_day, view_day, int.__eq__)
                or _base_order(first_seen_day, view_day, int.__ge__)
            ):
                arising = dict.get(record, "arising_position")
                if arising is None:
                    arising = dict.get(record, "position")
                if arising is None:
                    continue
                if not _whole(arising):
                    continue
                if _base_order(arising, as_of_position, int.__gt__):
                    continue
        _view_copy_guard(record)
        selected.append(_guarded_copy(record))
    return selected


def build_view_record(run_id="run-under-test", viewer_id="viewer-1",
                      day=1, contents=None, reputation_and_band=None,
                      graph_position=None, completeness="complete",
                      selection_rule_version="view-selection-1",
                      position=None, run_record=None, rule_version_set=None):
    """Write one ViewRecord in its decided field groups: identity
    and scope, content as references into retained records and as
    values for reputation, band, and graph position, arrival and
    freshness with its completeness state, the exclusion group as
    a form statement, and provenance naming the building
    component, the delivering contract, and the selection rule
    version. The record carries no position value of its own: its
    scheduling position is the position the run record handed in
    states for that day, and no position where none is handed in.
    The arrival group is derived from the contents handed in, item
    by item, and where an arrival value does not stand on a content
    record the group carries an explicit not derived marker in its
    place. A record carrying a barred field at any depth stands
    refused at this writing act. Content standing deeper than
    the view copy bound, or carrying a cycle, stands refused in
    the named failure form of the depth guard before any copy
    stands taken."""
    if completeness not in COMPLETENESS_STATES:
        raise NamedFailure("completeness state outside the closed vocabulary: " + str(completeness))
    if contents is None:
        contents = []
    elif isinstance(contents, (list, tuple)):
        contents = [item for index, item in _base_entries(contents)]
    else:
        raise NamedFailure(
            "view record writing refused in named form: contents stands "
            "in a non record sequence form and no view record stands "
            "written from it: " + type(contents).__name__
        )
    _view_copy_guard(contents)
    _view_copy_guard(reputation_and_band or {})
    _view_copy_guard(graph_position or {})
    stated_position = position
    if stated_position is None and isinstance(run_record, dict):
        stated_position = run_record.get("scheduling_position_identifier")
        if stated_position is None:
            stated_position = run_record.get("position")
        if stated_position is None:
            by_day = run_record.get("positions_by_day")
            if isinstance(by_day, dict):
                stated_position = by_day.get(str(day), by_day.get(day))
    first_seen = {}
    delays = {}
    derived = bool(contents)
    for index, item in enumerate(contents):
        seen_day = None
        applied = None
        if isinstance(item, dict):
            seen_day = item.get("first_seen_day", item.get("day"))
            applied = item.get("delay", item.get("delay_applied"))
        first_seen[str(index)] = seen_day
        delays[str(index)] = applied
        if seen_day is None or applied is None:
            derived = False
    record = {
        "run_identifier": run_id,
        "viewer_identifier": viewer_id,
        "simulated_day": day,
        "scheduling_position_identifier": stated_position,
        "rule_version_set": rule_version_set,
        "view_contents": [_freeze(item) for item in contents],
        "reputation_and_band_values": _freeze(reputation_and_band or {}),
        "graph_position_as_seen": _freeze(graph_position or {}),
        "first_seen_day_per_record": first_seen,
        "delay_applied_per_record": delays,
        "arrival_group_form": (
            "derived from contents" if derived
            else "not derived: an arrival value does not stand on every content record"
        ),
        "completeness_state": completeness,
        "building_component": "MOD-04 Tick Engine",
        "delivering_contract": "Contract K",
        "selection_rule_version": selection_rule_version,
        "exclusion_group": {
            "form_statement": "no barred field stands in a view record",
            "excluded": list(VIEW_EXCLUDED_CONTENT),
        },
        "form": "ViewRecord",
    }
    if view_record_carries_barred_field(record):
        raise NamedFailure(
            "a view record may not be written carrying a barred field at any depth"
        )
    return record


def view_record_carries_barred_field(view_record):
    """Return True where a ViewRecord carries a barred field at any
    depth of any of its groups, including the reputation and band
    group and content wrapped in lists."""
    if not isinstance(view_record, dict):
        return True
    stack = [view_record]
    visited = set()
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if id(node) in visited:
                continue
            visited.add(id(node))
            for key in dict.keys(node):
                if _is_barred_key(key):
                    return True
            for key, item in dict.items(node):
                if _is_barred_key(key):
                    return True
                stack.append(item)
        elif isinstance(node, (list, tuple, set, frozenset)):
            if id(node) in visited:
                continue
            visited.add(id(node))
            stack.extend(
                item for index, item in _base_entries(node))
    return False


def hold_view(view_record):
    """Hold one view at the hold point inside the tick: the
    ViewRecord stands written before delivery, and the view is
    released only after the Recorder leak check runner in MOD-10
    runs its three forms together on it and passes it, as
    release_view performs."""
    _view_copy_guard(view_record)
    return {"view_record": _guarded_copy(view_record), "held": True, "released": False}


def release_view(held, field_validation_passed=None, timing_passed=None):
    """Release a held view only where the Recorder leak check
    runner passes on the held record: the runner in MOD-10 runs
    all three forms together (canary, field validation, timing),
    and its result, not a caller supplied boolean, governs the
    release. The two boolean arguments stand accepted for the
    standing call form and govern nothing. A view the runner
    refuses is not delivered, and the refusal names the view, the
    field, and the check form that failed, in the runner words.
    No agent act inside the same simulated day rests on a view
    that is not delivered."""
    from crucible import mod10

    view_record = held.get("view_record") if isinstance(held, dict) else None
    try:
        check = mod10.run_view_leak_check(view_record)
    except ValueError as exc:
        raise NamedFailure(str(exc)) from exc
    released = dict(held)
    released["held"] = False
    released["released"] = True
    released["leak_check"] = check
    return released


def write_checkpoint(manifest, agent_states=None,
                     escrow_contract_states=None, detection_state=None,
                     stream_positions_and_generator_states=None,
                     simulation_clock_value=None):
    """Write one checkpoint: the CheckpointState of Form 13A
    beside its manifest, in the same act, so that manifest and
    state describe one state or neither stands. The state carries
    the run identifier and simulated day of its manifest and the
    state parts as handed in; a state part standing unhanded, or
    a state failing Form 13A validation, stands refused in named
    form before any retention, and neither the manifest nor the
    state stands retained. The pair stands retained through the
    Recorder paired store in MOD-10, where the state reads back
    beside the manifest."""
    from crucible import mod01, mod10

    if not isinstance(manifest, dict):
        raise NamedFailure(
            "checkpoint writing in named form: a checkpoint stands "
            "on a manifest record, and no other form stands written")
    run_id = manifest.get("run_identifier") or manifest.get("run_id")
    day = manifest.get("simulated_day")
    if run_id is None or day is None:
        raise NamedFailure(
            "checkpoint writing in named form: no run identifier or "
            "no simulated day stands on the manifest, and no "
            "checkpoint stands written under no identity")
    state = {
        "run_identifier": run_id,
        "simulated_day": day,
        "agent_states": _freeze(agent_states),
        "escrow_contract_states": _freeze(escrow_contract_states),
        "detection_state": _freeze(detection_state),
        "stream_positions_and_generator_states": _freeze(
            stream_positions_and_generator_states),
        "simulation_clock_value": simulation_clock_value,
    }
    missing = [
        field for field in mod01.form_fields("13A")
        if state.get(field) is None
    ]
    if missing:
        raise NamedFailure(
            "checkpoint writing in named form: the CheckpointState "
            "carries no " + ", ".join(missing)
            + ", and neither the manifest nor the state stands written")
    if not mod01.validate_record("13A", state):
        raise NamedFailure(
            "checkpoint writing in named form: the CheckpointState "
            "fails Form 13A validation, and neither the manifest "
            "nor the state stands written")
    paired = _freeze(manifest)
    paired["checkpoint_state"] = copy.deepcopy(state)
    mod10.retain_checkpoint(paired)
    return {"manifest": paired, "checkpoint_state": state}


def per_viewer_components(run_id="run-under-test", viewers=None, components=None):
    """The per viewer components of one run: every component
    carries its viewer identifier, and no component stands as a
    singular vector. Where components stand handed in, they stand
    returned per viewer in the order given."""
    if components is not None:
        return [_freeze(item) for item in components]
    viewers = list(viewers or ("viewer-1", "viewer-2"))
    result = []
    for index, viewer in enumerate(viewers):
        result.append({
            "run_id": run_id,
            "viewer_id": viewer,
            "component_values": [index + 1, index + 2, index + 3, index + 4],
            "presented_as": "per viewer component",
        })
    return result


def divergence_companion(run_id="run-under-test", components=None):
    """The viewer divergence companion: beside the per viewer form,
    in the daily aggregates and at end of run, the share of
    identities whose band differs across viewers. A view
    independent component records its coincidence as a nil
    divergence for that component, never as a singular value."""
    components = components if components is not None else per_viewer_components(run_id)
    components = [item for item in components if isinstance(item, dict)]
    viewers = set()
    bands_by_identity = {}
    viewers_by_identity = {}
    completeness = set()
    stated = bool(components)
    for component in components:
        viewer = component.get("viewer_id")
        if viewer is None:
            viewer = component.get("viewer_identifier")
        if viewer is not None:
            viewers.add(viewer)
        identity = component.get("identity")
        if identity is None:
            identity = component.get("agent_identifier")
        if identity is None:
            identity = component.get("identity_identifier")
        band = component.get("band")
        if identity is None or band is None:
            stated = False
            continue
        bands_by_identity.setdefault(identity, set()).add(band)
        viewers_by_identity.setdefault(identity, set()).add(viewer)
        if component.get("completeness_state") is not None:
            completeness.add(component.get("completeness_state"))
    identity_count = len(bands_by_identity)
    differing = sum(
        1 for bands in bands_by_identity.values() if len(bands) > 1
    )
    missing = sum(
        len(viewers) - len(viewers_by_identity.get(identity, ()))
        for identity in bands_by_identity
    )
    if stated and identity_count:
        share = differing / identity_count
        share_form = "share of identities whose band differs across viewers"
    else:
        share = None
        share_form = "unknown: no band stands to compare for every identity"
    companion_entry = {
        "band_differing_share": share,
        "share_form": share_form,
        "differing_identity_count": differing if stated else None,
        "identity_count": identity_count if stated else None,
        "missing_count": missing if stated else None,
        "viewer_count": len(viewers),
        "completeness_states": sorted(completeness) if completeness else ["not stated"],
        "form": "divergence companion",
        "singular_vector_reported": False,
    }
    return {
        "run_id": run_id,
        "daily_aggregates": dict(companion_entry),
        "end_of_run": dict(companion_entry),
        "band_differing_share": share,
        "differing_identity_count": companion_entry["differing_identity_count"],
        "identity_count": companion_entry["identity_count"],
        "missing_count": companion_entry["missing_count"],
        "viewer_count": len(viewers),
        "completeness_states": companion_entry["completeness_states"],
    }


def flip_trial_record(trial_id="trial-under-test", candidate_forms=None):
    """The viewer flip trial record: it reports a property of
    candidate forms, restates the bar on a singular presentation
    on its face, and is never a run result."""
    return {
        "trial_id": trial_id,
        "kind": "property_of_candidate_forms",
        "candidate_forms": list(candidate_forms or ("per viewer form", "singular form")),
        "property": "whether a candidate form presents one comparable vector quantity",
        "singular_presentation_bar": (
            "no singular vector is reported and the vector is not "
            "presented as one comparable quantity in any run"
        ),
        "run_result": False,
    }

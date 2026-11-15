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
import itertools
import unicodedata

__all__ = [
    "BARRED_PROJECTION_KEYS",
    "CANARY_VALUE",
    "CLEANING_DEPTH_BOUND",
    "COMPLETENESS_STATES",
    "EVENT_KINDS",
    "GATED_FAILURE_NAME",
    "GATE_EXECUTABLE_RUNS",
    "PROCESSING_TYPES",
    "PROJECTION_KEYS",
    "PROTOTYPE_ORDER",
    "VALUE_APPEARS_DEPTH_BOUND",
    "VIEW_CLOSED_FIELDS",
    "VIEW_COPY_DEPTH_BOUND",
    "VIEW_EXCLUDED_CONTENT",
    "AlterationBarred",
    "ContractAHandover",
    "DeliveryPoint",
    "DetectionLayerDeliveryPoint",
    "GatedRun",
    "NamedFailure",
    "RuleCoreDeliveryPoint",
    "TickEngine",
    "apply_event_to_state",
    "build_tracer_run_record",
    "build_view_record",
    "canary_appears_in_projection",
    "delivery_completeness",
    "divergence_companion",
    "exercise_f09_canary",
    "flip_trial_record",
    "headline_order_stands",
    "hold_view",
    "is_processing_type",
    "measure_order_sensitivity",
    "per_viewer_components",
    "process_day_events",
    "project_detection_input",
    "projection_passed_for_run",
    "release_view",
    "run",
    "run_is_reportable",
    "run_record_with_order",
    "run_tracer_cut",
    "scheduling_order_record",
    "select_view_records",
    "tick",
    "validate_run_scheduling_order",
    "view_record_carries_barred_field",
    "write_checkpoint",
]

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


def _freeze(value, _memo=None):
    """Freeze one value through base class readings and plain
    constructors only, in the form the guarded copy of this
    module states: a set or frozenset part stands rebuilt by the
    plain set or plain frozenset constructor over its base
    iteration reading, and a part in no container form stands
    copied as itself, so a constructor or a copy protocol a part
    itself supplies is never called on a part this act copies.
    An act that freezes several handed values into one assembled
    result hands one shared memo through every freeze, so a part
    shared between those values stands in the assembled result
    as one copy, never as a separate copy per value."""
    return _guarded_copy(value, _memo)


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
        if id(value) in _memo:
            return _memo[id(value)]
        copied = tuple(
            _guarded_copy(item, _memo) for item in tuple.__iter__(value))
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, frozenset):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = frozenset(
            _guarded_copy(item, _memo) for item in frozenset.__iter__(value))
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
            copied.add(_guarded_copy(item, _memo))
        return copied
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
        _view_copy_guard(point, _act="ContractAHandover", _argument="point")
        _view_copy_guard(assumption_record, _act="ContractAHandover", _argument="assumption_record")
        _view_copy_guard(seed_input_set, _act="ContractAHandover", _argument="seed_input_set")
        _view_copy_guard(family_id, _act="ContractAHandover", _argument="family_id")
        memo = {}
        object.__setattr__(self, "_point", _freeze(point, memo))
        object.__setattr__(self, "_assumption_record", _freeze(assumption_record, memo))
        object.__setattr__(self, "_seed_input_set", _freeze(seed_input_set, memo))
        object.__setattr__(self, "_family_id", _freeze(family_id, memo))
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
        differing = []
        if not point == self._point:
            differing.append("point")
        if not assumption_record == self._assumption_record:
            differing.append("assumption_record (the assumption record)")
        if not seed_input_set == self._seed_input_set:
            differing.append("seed_input_set (the seed input set)")
        if not family_id == self._family_id:
            differing.append("family_id (the family identifier)")
        if differing:
            raise AlterationBarred(
                "silent correction inside the Engine: the "
                + " and the ".join(differing)
                + " handed value differs from the Contract A handover"
            )
        return True

    def as_dict(self):
        memo = {}
        return {
            "point": _freeze(self._point, memo),
            "assumption_record": _freeze(self._assumption_record, memo),
            "seed_input_set": _freeze(self._seed_input_set, memo),
            "family_id": _freeze(self._family_id, memo),
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
        _view_copy_guard(payload_description, _act="DeliveryPoint.record_interface_delivery", _argument="payload_description")
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
            if dict.__contains__(state, name):
                return dict.__getitem__(state, name)
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
    "а": "a", "с": "c", "е": "e", "о": "o",
    "р": "p", "х": "x", "у": "y", "і": "i",
    "ј": "j", "ѕ": "s", "һ": "h", "к": "k",
    "м": "m", "н": "h", "т": "t", "в": "b",
    "α": "a", "β": "b", "ε": "e", "ι": "i",
    "κ": "k", "μ": "m", "ο": "o", "ρ": "p",
    "τ": "t", "χ": "x", "υ": "y", "ν": "n",
    "γ": "g", "δ": "d", "λ": "l", "σ": "s",
    "ω": "w", "ζ": "z", "θ": "t", "φ": "f",
    "æ": "ae", "œ": "oe", "ø": "o", "đ": "d",
    "ł": "l", "ß": "ss", "þ": "th", "ð": "d",
    "ħ": "h", "ŋ": "n", "ƒ": "f", "ı": "i",
    "ŧ": "t",
    "Æ": "ae", "Œ": "oe", "Ø": "o", "Đ": "d",
    "Ł": "l", "ẞ": "ss", "Þ": "th", "Ð": "d",
    "Ħ": "h", "Ŋ": "n", "Ƒ": "f", "Ŧ": "t",
    "б": "b", "г": "g", "д": "d", "и": "i",
    "п": "p", "η": "e", "π": "p", "ς": "s",
    "օ": "o", "Օ": "o", "ւ": "n", "Ո": "n",
    "ᴀ": "a", "ʙ": "b", "ᴄ": "c", "ᴅ": "d",
    "ᴇ": "e", "ꜰ": "f", "ɢ": "g", "ʜ": "h",
    "ɪ": "i", "ᴊ": "j", "ᴋ": "k", "ʟ": "l",
    "ᴍ": "m", "ɴ": "n", "ᴏ": "o", "ᴘ": "p",
    "ꞯ": "q", "ʀ": "r", "ꜱ": "s", "ᴛ": "t",
    "ᴜ": "u", "ᴠ": "v", "ᴡ": "w", "ʏ": "y",
    "ᴢ": "z",
    "ᴇ": "e", "ʟ": "l", "ᴏ": "o", "ᴛ": "t",
    "ђ": "s", "ѓ": "h",
    "Ꮢ": "r", "ꪖ": "r", "Ꮼ": "e", "ꫜ": "e",
    "Ꭺ": "a", "ꪊ": "a", "Ꮮ": "l", "ꪮ": "l",
    "Ꮟ": "m", "ꪇ": "m", "Ᏸ": "o", "ꪎ": "o",
    "Ꮑ": "n", "ꪑ": "n", "Ꮿ": "y", "꪿": "y",
    "ⲣ": "r", "ⲉ": "e", "ⲁ": "a", "ⲗ": "l",
    "ⲙ": "m", "ⲟ": "o", "ⲛ": "n", "ⲩ": "y",
    "€": "e", "£": "l", "!": "l", "|": "l", "¥": "y",
    "¢": "c", "§": "s", "+": "t",
}
# Transcription repair, stated in the open: entries of this map
# stand keyed in this copy by a neighbouring codepoint in place
# of the codepoint the merged tree records, and the four
# modifier letter entries stand missing. Each entry stands set
# here to its recorded codepoint, by number, before the
# uppercase pass below runs, so the map this copy builds is the
# map the merged tree builds.
for _recorded, _reading, _neighbour in (
        (0x0493, "h", 0x0453), (0x0578, "n", 0x0552),
        (0x0548, "n", 0x0582), (0x13AC, "e", 0x13EC),
        (0x13B7, "m", 0x13CF), (0x13BE, "o", 0x13F0),
        (0xABA2, "r", 0xAA96), (0xAB7C, "e", 0xAADC),
        (0xAB7A, "a", 0xAA8A), (0xABAE, "l", 0xAAAE),
        (0xAB87, "m", 0xAA87), (0xAB8E, "o", 0xAA8E),
        (0xAB91, "n", 0xAA91), (0xABBF, "y", 0xAABF),
        (0x1D31, "e", None), (0x1D38, "l", None),
        (0x1D3C, "o", None), (0x1D40, "t", None)):
    if _neighbour is not None:
        _HOMOGLYPH_MAP.pop(chr(_neighbour), None)
    _HOMOGLYPH_MAP[chr(_recorded)] = _reading
for _upper, _lower in list(_HOMOGLYPH_MAP.items()):
    _HOMOGLYPH_MAP[_upper.upper()] = _lower

_TRANSLITERATION_MAP = {
    "а": "a", "б": "b", "в": "v", "г": "g",
    "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "h", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "", "ы": "y", "ь": "", "э": "e",
    "ю": "yu", "я": "ya",
    "ѕ": "s", "һ": "h", "і": "i",
    "ђ": "s", "ѓ": "h",
    "Ꮢ": "r", "ꪖ": "r", "Ꮼ": "e", "ꫜ": "e",
    "Ꭺ": "a", "ꪊ": "a", "Ꮮ": "l", "ꪮ": "l",
    "Ꮟ": "m", "ꪇ": "m", "Ᏸ": "o", "ꪎ": "o",
    "Ꮑ": "n", "ꪑ": "n", "Ꮿ": "y", "꪿": "y",
    "ⲣ": "r", "ⲉ": "e", "ⲁ": "a", "ⲗ": "l",
    "ⲙ": "m", "ⲟ": "o", "ⲛ": "n", "ⲩ": "y",
    "α": "a", "β": "b", "γ": "g", "δ": "d",
    "ε": "e", "ζ": "z", "η": "e", "θ": "th",
    "ι": "i", "κ": "k", "λ": "l", "μ": "m",
    "ν": "n", "ο": "o", "π": "p", "ρ": "r",
    "ς": "s", "σ": "s", "τ": "t", "υ": "u",
    "φ": "ph", "χ": "h", "ψ": "ps", "ω": "o",
    "æ": "ae", "œ": "oe", "ø": "o", "đ": "d",
    "ł": "l", "ß": "ss", "þ": "th", "ð": "d",
    "ħ": "h", "ŋ": "n", "ƒ": "f", "ı": "i",
    "ŧ": "t",
    "ᴀ": "a", "ʙ": "b", "ᴄ": "c", "ᴅ": "d",
    "ᴇ": "e", "ꜰ": "f", "ɢ": "g", "ʜ": "h",
    "ɪ": "i", "ᴊ": "j", "ᴋ": "k", "ʟ": "l",
    "ᴍ": "m", "ɴ": "n", "ᴏ": "o", "ᴘ": "p",
    "ꞯ": "q", "ʀ": "r", "ꜱ": "s", "ᴛ": "t",
    "ᴜ": "u", "ᴠ": "v", "ᴡ": "w", "ʏ": "y",
    "ᴢ": "z",
    "ᴇ": "e", "ʟ": "l", "ᴏ": "o", "ᴛ": "t",
    "օ": "o", "Օ": "o", "ւ": "n", "Ո": "n",
    "@": "a", "€": "e", "£": "l", "!": "l", "|": "l",
    "¥": "y", "$": "s", "¢": "c", "§": "s", "+": "t",
}
# Transcription repair, stated in the open, in the form of the
# repair at the homoglyph map above: each entry stands set here
# to its recorded codepoint, by number, before the uppercase
# pass below runs.
for _recorded, _reading, _neighbour in (
        (0x0493, "h", 0x0453), (0x0578, "n", 0x0552),
        (0x0548, "n", 0x0582), (0x13AC, "e", 0x13EC),
        (0x13B7, "m", 0x13CF), (0x13BE, "o", 0x13F0),
        (0xABA2, "r", 0xAA96), (0xAB7C, "e", 0xAADC),
        (0xAB7A, "a", 0xAA8A), (0xABAE, "l", 0xAAAE),
        (0xAB87, "m", 0xAA87), (0xAB8E, "o", 0xAA8E),
        (0xAB91, "n", 0xAA91), (0xABBF, "y", 0xAABF),
        (0x1D31, "e", None), (0x1D38, "l", None),
        (0x1D3C, "o", None), (0x1D40, "t", None)):
    if _neighbour is not None:
        _TRANSLITERATION_MAP.pop(chr(_neighbour), None)
    _TRANSLITERATION_MAP[chr(_recorded)] = _reading
for _upper, _lower in list(_TRANSLITERATION_MAP.items()):
    _TRANSLITERATION_MAP[_upper.upper()] = _lower

_LEET_MAP = {
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s",
    "€": "e", "£": "l", "!": "l", "|": "l", "¥": "y",
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


def _stored_text(value):
    """The text a value stores, read through the base class
    string form, never through a string reading the value
    itself supplies. A value that is not a text form stores
    no text, so no name stands judged from a string reading
    a non text value itself supplies, and its stored text
    stands as the empty text, in the cured no name form the
    sister modules state. A bytes, bytearray, or memoryview
    value stands judged on its stored bytes, read through the
    buffer the value stores and decoded as UTF-8 with
    undecodable bytes dropped, never through a string reading
    a bytes subclass itself supplies, so a bytes like form
    keeps the standing its stored name carries, in the same
    form the condition and passage limbs of this estate judge
    those forms."""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, (bytes, bytearray, memoryview)):
        return bytes.decode(bytes(value), "utf-8", "ignore")
    return ""


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
        "NFKD", _stored_text(key).lower()).lower()
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
            # The digit readings mixed position by position: the
            # leet reading stands taken at each digit position
            # that carries one, and a digit carrying no leet
            # reading stands dropped at its own position, so a
            # word needing the leet reading at one digit position
            # and the drop reading at another stands read whole.
            "".join(character for character in leet_applied_first
                    if character.isalpha()),
            "".join(character for character in leet_one_as_i
                    if character.isalpha()),
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
            for character in _stored_text(key).lower()
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
    for character in _stored_text(key).lower():
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
        if character == "й":
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


def _character_variants(character):
    """Every folded form one original character can contribute
    to a combined reading: each reading the combination limb of
    _folded_readings records for the character, taken under the
    readings _add_readings states inside that function, so the
    leet reading at one position and the drop reading at
    another combine inside one key."""
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
    if character == "й":
        options.update(("y", "i"))
    variants = set()
    for option in options:
        plain = "".join(
            part for part in option if part.isalnum())
        leet_first = "".join(
            part for part in "".join(
                _LEET_MAP.get(part, part) for part in option)
            if part.isalnum())
        leet_i = "".join(
            part for part in "".join(
                "i" if part == "1"
                else _LEET_MAP.get(part, part)
                for part in option)
            if part.isalnum())
        variants.update((
            plain,
            leet_first,
            leet_i,
            "".join(part for part in plain if not part.isdigit()),
            "".join(part for part in leet_first if part.isalpha()),
            "".join(part for part in leet_i if part.isalpha()),
        ))
    return variants


def _combined_matches_exact(variant_sets, target):
    states = {0}
    for variants in variant_sets:
        following = set()
        for state in states:
            for variant in variants:
                if target.startswith(variant, state):
                    following.add(state + len(variant))
        states = following
        if not states:
            return False
    return len(target) in states


def _combined_prefix_state(pattern, state, character):
    candidate = pattern[:state] + character
    limit = min(len(pattern), state + 1)
    for length in range(limit, -1, -1):
        if candidate.endswith(pattern[:length]):
            return length
    return 0


def _combined_carries(variant_sets, pattern):
    full = len(pattern)
    states = {0}
    for variants in variant_sets:
        following = set()
        for state in states:
            for variant in variants:
                current = state
                for character in variant:
                    if current == full:
                        break
                    current = _combined_prefix_state(
                        pattern, current, character)
                following.add(current)
        if full in following:
            return True
        states = following
    return full in states


def _combined_key_barred(key):
    """Whether any combined reading of the key stands barred,
    judged position by position over the per character variants
    without enumerating the combined texts, so the judgement
    stands the same inside the 4096 combined text bound and
    past it, in the form the MOD-05 read takes. The forms
    judged are the forms _is_barred_key judges on an enumerated
    reading: a reading standing in the folded exact set of the
    barred keys, and a reading carrying a folded barred part."""
    variant_sets = [
        _character_variants(character)
        for character in _stored_text(key).lower()
    ]
    for target in _BARRED_FOLDED_EXACT:
        if _combined_matches_exact(variant_sets, target):
            return True
    for part in _BARRED_FOLDED_PARTS:
        if _combined_carries(variant_sets, part):
            return True
    return False


def _is_barred_text(key):
    """Whether one non container key stands barred, judged on
    its stored text through the folded readings."""
    lowered = _stored_text(key).lower()
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
    return _combined_key_barred(key)



_UNORDERED_JOIN_PART_BOUND = 7

_JOIN_CANDIDATE_BOUND = 5040

_SEG_JOIN_CANDIDATE_BOUND = 131072

_SEG_FOLDED_CANDIDATE_BOUND = 20000


def _join_container_parts(node):
    """The parts a container stores, read through base class
    operations only, in the iteration order the container
    stands in for this process."""
    return [item for index, item in _base_entries(node)]


def _has_unordered_split(value):
    """Whether a key carries a set or frozenset part holding
    two or more parts, found on an iterative walk, so no
    recursion stands spent on a key that carries none."""
    seen = set()
    stack = [value]
    while stack:
        node = stack.pop()
        if isinstance(node, (dict, tuple, list, set, frozenset)):
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
            if not isinstance(node, (tuple, list, set, frozenset)):
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
        if isinstance(node, (dict, tuple, list, set, frozenset)):
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
    if not isinstance(node, (tuple, list, set, frozenset)):
        if folded:
            readings = set(_folded_readings(node))
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
        return set(_folded_readings(node))
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
        if _universe is not None and isinstance(part, (tuple, list, set, frozenset)):
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
            readings.update(_folded_readings(text))
        if not readings:
            readings = {""}
        if _universe is not None and isinstance(part, (tuple, list, set, frozenset)):
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
    under this module scalar barred judgement, judged by
    segmentation beside the kept candidate readings. The plain
    limb tiles the plain exact names and the plain barred parts
    of the scalar judgement over the lowered joined texts of
    the parts; the folded limb tiles its folded exact names
    and folded barred parts over the folded readings of the
    parts. Either limb standing barred bars the key, as a
    joined candidate standing barred bars it."""
    for node, parts in _seg_unordered_nodes(key):
        plain_universe = _seg_universe(
            BARRED_PROJECTION_KEYS, _BARRED_KEY_PARTS)
        plain = _seg_plain_options(
            parts, plain_universe, _seg_prefixes(plain_universe))
        for target in tuple(BARRED_PROJECTION_KEYS):
            if _seg_tiles_exact(plain, target):
                return True
        for pattern in tuple(_BARRED_KEY_PARTS):
            if _seg_tiles_carrying(plain, pattern) is not None:
                return True
        for pattern in tuple(_BARRED_KEY_PARTS):
            if _seg_parts_carry_edge(parts, plain, pattern, False):
                return True
        folded_universe = _seg_universe(
            _BARRED_FOLDED_EXACT, _BARRED_FOLDED_PARTS)
        folded = _seg_folded_options(
            parts, folded_universe, _seg_prefixes(folded_universe))
        for target in tuple(_BARRED_FOLDED_EXACT):
            if _seg_tiles_exact(folded, target):
                return True
        for pattern in tuple(_BARRED_FOLDED_PARTS):
            if _seg_tiles_carrying(folded, pattern) is not None:
                return True
        for pattern in tuple(_BARRED_FOLDED_PARTS):
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



def _is_barred_key(key, _seen=None):
    if isinstance(key, (dict, tuple, list, set, frozenset)):
        # A container key stores no text name of its own. It
        # stands barred only where a part it stores stands
        # barred, judged on the stored parts through their base
        # readings, or where the stored text parts joined in
        # order spell a barred name, never from a string reading
        # the container itself supplies. The joined reading
        # stands built post order on an explicit stack of
        # frames, so the joined text of a nested container
        # stands carried up into the joined text of the
        # container that holds it, and a barred name split
        # between a nested container and its sibling stands
        # judged on the whole joined reading, in the form the
        # MOD-03 walk states. A dict stands read by its keys,
        # as the sister modules read it. The stored text of a
        # part stands read through _stored_text, so a part in
        # bytes, bytearray, or memoryview dress contributes its
        # decoded stored text to the joined reading exactly as
        # a text part does, and a single part container carries
        # the reading of its one part. No recursion stands
        # spent on the walk, so a container key nested to any
        # depth the walk can hold stands answered both ways
        # and no bare RecursionError escapes this predicate or
        # any public act that reads through it.
        joined_cache = {}

        def scalar_barred(text):
            if text not in joined_cache:
                joined_cache[text] = _is_barred_text(text)
            return joined_cache[text]

        def container_items(container):
            if isinstance(container, dict):
                return list(dict.keys(container))
            return [item for index, item in _base_entries(container)]

        active = set()
        frames = []

        def push(container):
            frames.append(
                [id(container), container_items(container),
                 0, [], False])
            active.add(id(container))

        push(key)
        result = False
        while frames:
            frame = frames[-1]
            container_id, items, index, joined_parts, barred = frame
            if index < len(items):
                frame[2] = index + 1
                part = items[index]
                if isinstance(
                        part, (dict, tuple, list, set, frozenset)):
                    if id(part) in active:
                        continue
                    push(part)
                else:
                    if _is_barred_text(part):
                        frame[4] = True
                    joined_parts.append(_stored_text(part))
            else:
                joined = "".join(joined_parts)
                barred_here = barred or (
                    bool(joined) and scalar_barred(joined))
                frames.pop()
                active.discard(container_id)
                if frames:
                    parent = frames[-1]
                    parent[3].append(joined)
                    if barred_here:
                        parent[4] = True
                else:
                    result = barred_here
        if not result and _has_unordered_split(key):
            for candidate in _joined_text_candidates(key):
                if candidate and _is_barred_text(candidate):
                    return True
        if not result and _seg_unordered_barred(key):
            return True
        if not result and _seg_spanning_barred(
                key, tuple(BARRED_PROJECTION_KEYS),
                tuple(_BARRED_KEY_PARTS), tuple(_BARRED_FOLDED_EXACT),
                tuple(_BARRED_FOLDED_PARTS)):
            return True
        return result
    return _is_barred_text(key)


CLEANING_DEPTH_BOUND = 100

VALUE_APPEARS_DEPTH_BOUND = 100


def _clean_leaf_copy(value):
    """Copy one leaf part of a projection through no protocol the
    part itself supplies. A leaf part stands copied as itself, so
    a part carrying a lying deepcopy protocol cannot materialise
    as another value inside the delivered projection."""
    return value


def _clean_value(value, _depth=0, _seen=None, _path=""):
    """Clean one value for the projection. A container shared by
    two siblings stands cleaned once at each depth at which it
    stands reached: its cleaned form stands carried across every
    path that reaches it at that depth, so the walk grows with
    the size of the value, and a reach at a greater depth stands
    recleaned at its own depth, where the cleaning bound is
    judged afresh. A container standing on its own walk path
    stands as a cycle and stands refused in the named form."""
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > CLEANING_DEPTH_BOUND:
            raise NamedFailure(
                "projection cleaning bound reached at " + (_path or "root")
                + ": the value stands deeper than the stated bound of "
                + str(CLEANING_DEPTH_BOUND)
                + ", counting every container standing around the "
                "handed value within the value being cleaned toward "
                "that bound, and no cleaning stands performed on "
                "the handed value"
            )
        if isinstance(_seen, dict):
            state = _seen
        else:
            state = {"active": set(_seen or ()), "done": {}}
        marker = (id(value), _depth)
        if marker in state["done"]:
            return state["done"][marker]
        if id(value) in state["active"]:
            raise NamedFailure(
                "projection cleaning found a cycle at " + (_path or "root")
                + ", and no cleaning stands performed on the cyclic value"
            )
        state["active"].add(id(value))
        try:
            if isinstance(value, dict):
                if _is_barred_key(value) and not any(
                        _is_barred_key(key)
                        for key in dict.keys(value)):
                    result = {}
                else:
                    result = {
                        _clean_value(
                            key, _depth + 1, state, _path + "/" + str(key)):
                        _clean_value(item, _depth + 1, state, _path + "/" + str(key))
                        for key, item in dict.items(value)
                        if not _is_barred_key(key)
                    }
            elif isinstance(value, list):
                result = [
                    _clean_value(item, _depth + 1, state, _path + "[" + str(index) + "]")
                    for index, item in _base_entries(value)
                ]
            elif isinstance(value, tuple):
                result = tuple(
                    _clean_value(item, _depth + 1, state, _path + "[" + str(index) + "]")
                    for index, item in _base_entries(value)
                )
            elif isinstance(value, set):
                result = set(
                    _clean_value(item, _depth + 1, state, _path + "[" + str(index) + "]")
                    for index, item in _base_entries(value)
                )
            else:
                result = frozenset(
                    _clean_value(item, _depth + 1, state, _path + "[" + str(index) + "]")
                    for index, item in _base_entries(value)
                )
            state["done"][marker] = result
            return result
        finally:
            state["active"].discard(id(value))
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
            path = "[" + str(index) + "]"
            if isinstance(item, dict):
                # A record in record form stands as the slot
                # wrapper, as the feature values record stands
                # for a feature value, so the wrapper itself
                # counts nothing toward the bound and every value
                # the record holds stands cleaned from the same
                # first depth a feature value stands cleaned
                # from: a value under a key of one record stands
                # judged at the same depth as the same value
                # under a key of the feature values. A record in
                # no record form stands cleaned as itself, in
                # full, at that same first depth.
                state = {"active": set(), "done": {}}
                record = {}
                for key, value in dict.items(item):
                    if _is_barred_key(key):
                        continue
                    cleaned_key = _clean_value(
                        key, 1, state, path + "/" + str(key))
                    record[cleaned_key] = _clean_value(
                        value, 1, state, path + "/" + str(key))
                cleaned.append(record)
            else:
                cleaned.append(_clean_value(item, 1, None, path))
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


def _value_appears(value, node, _seen=None, _depth=0, _walked=None):
    if _walked is None:
        _walked = {}
    if isinstance(node, (dict, list, tuple, set, frozenset)):
        if _depth > VALUE_APPEARS_DEPTH_BOUND:
            raise NamedFailure(
                "canary presence read bound reached: the value stands "
                "deeper than the stated bound of "
                + str(VALUE_APPEARS_DEPTH_BOUND)
                + ", counted with every container standing around a "
                "part counting toward that bound, and no presence "
                "answer stands"
            )
        seen = _seen if _seen is not None else set()
        if id(node) in seen:
            raise NamedFailure(
                "canary presence read found a cycle: the value stands "
                "in a cycle and no presence answer stands"
            )
        walked_key = (id(node), _depth)
        if walked_key in _walked:
            return _walked[walked_key]
        seen.add(id(node))
        try:
            if node == value:
                result = True
            elif isinstance(node, dict):
                result = any(
                    _value_appears(value, v, seen, _depth + 1, _walked)
                    for v in dict.values(node)
                ) or any(
                    _value_appears(value, k, seen, _depth + 1, _walked)
                    for k in dict.keys(node)
                )
            else:
                result = any(
                    _value_appears(value, item, seen, _depth + 1, _walked)
                    for index, item in _base_entries(node)
                )
        finally:
            seen.discard(id(node))
        _walked[walked_key] = result
        return result
    if node == value:
        return True
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
        _view_copy_guard(change, _act="TickEngine.write_simulation_state", _argument="change")
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
    _view_copy_guard(run_record, _act="run_record_with_order", _argument="run_record")
    _view_copy_guard(order_identifier, _act="run_record_with_order", _argument="order_identifier")
    memo = {}
    record = _freeze(run_record, memo)
    record["scheduling_order_identifier"] = _freeze(order_identifier, memo)
    return record


def validate_run_scheduling_order(record):
    """Return True only where a run record may stand on its order.

    Every run record states the order it used. A headline run whose
    scheduling order identifier is absent, or reads prototype,
    fails, per operation C-14 and open point OP-08.
    """
    if not isinstance(record, dict):
        return False
    order = dict.get(record, "scheduling_order_identifier")
    if not order:
        return False
    if dict.get(record, "run_class") == "headline" and order == PROTOTYPE_ORDER:
        return False
    return True


def headline_order_stands(record):
    """Return True only where a headline run order stands stated
    and is not a prototype order."""
    if not isinstance(record, dict):
        return False
    if dict.get(record, "run_class") != "headline":
        return False
    order = dict.get(record, "scheduling_order_identifier")
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
    _view_copy_guard(event, _act="apply_event_to_state", _argument="event")
    if isinstance(state, dict):
        _view_copy_guard(state, _act="apply_event_to_state", _argument="state")
    engine.write_simulation_state(engine, {"event": _freeze(event)})
    updated = _freeze(state) if isinstance(state, dict) else {}
    updates = dict.get(event, "feature_updates") if isinstance(event, dict) else None
    if isinstance(updates, dict):
        _view_copy_guard(updates, _act="apply_event_to_state", _argument="feature_updates")
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
    if isinstance(state, dict):
        _view_copy_guard(state, _act="process_day_events", _argument="state")
    current = _freeze(state) if isinstance(state, dict) else {}
    projections = []
    for position, event in enumerate(events):
        _view_copy_guard(
            event, _act="process_day_events",
            _argument="event at position " + str(position))
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
    delivered_kinds = []
    for entry in deliveries:
        if not isinstance(entry, dict):
            continue
        delivered_event = dict.get(entry, "event")
        if not isinstance(delivered_event, dict):
            continue
        delivered_kinds.append(dict.get(delivered_event, "kind"))
    expected = [
        dict.get(event, "kind") if isinstance(event, dict) else None
        for event in events
    ]
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
    return dict.get(run_record, "projection_canary_passed") is True


def run_is_reportable(run_record):
    """A run is reportable only where its projection passed the
    canary test and its scheduling order stands for its class."""
    if not isinstance(run_record, dict):
        return False
    return (
        projection_passed_for_run(run_record)
        and validate_run_scheduling_order(run_record)
        and dict.get(run_record, "reportable") is not False
        and dict.get(run_record, "form") != "form_only"
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


def _view_copy_guard(value, _depth=0, _seen=None, _path="", _walked=None,
                     _act=None, _argument=None):
    """Walk a value the view select and build acts are about to
    copy, under the same depth bound and named failure form as
    the TA-03 cures: a value standing deeper than the bound, or
    carrying a cycle, raises NamedFailure naming the bound or
    the cycle at its path, and no bare RecursionError escapes
    the copy. A value shared from two places on different paths
    carries no cycle and stands admitted. The walk carries a
    walked standing across paths, keyed by the container and
    the depth it stands walked at, so a container stands walked
    once for the paths that reach it at that depth and a deeper
    reach still stands judged at its own depth. Every refusal
    names the act that refused and the argument it refused, so
    refusals at different acts, and at different arguments of
    one act, stand told apart. The bound counts the depth of
    the value as it stands in the record the act builds, so
    every container standing around the handed value in that
    record counts toward the bound, and the refusal states
    that counting in its wording."""
    if _walked is None:
        _walked = set()
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        if _depth > VIEW_COPY_DEPTH_BOUND:
            raise NamedFailure(
                "view record copy bound reached at " + (_path or "root")
                + ": the value stands deeper than the stated bound of "
                + str(VIEW_COPY_DEPTH_BOUND)
                + ", counting every container standing around the "
                "handed value in the record the act builds toward "
                "that bound"
                + _guard_context(_act, _argument)
            )
        seen = _seen if _seen is not None else set()
        if id(value) in seen:
            raise NamedFailure(
                "view record copy found a cycle at " + (_path or "root")
                + _guard_context(_act, _argument)
            )
        if (id(value), _depth) in _walked:
            return
        seen.add(id(value))
        try:
            if isinstance(value, dict):
                for key, item in dict.items(value):
                    _view_copy_guard(
                        key, _depth + 1, seen, _path + "/" + str(key),
                        _walked, _act, _argument)
                    _view_copy_guard(
                        item, _depth + 1, seen, _path + "/" + str(key),
                        _walked, _act, _argument)
            else:
                for index, item in _base_entries(value):
                    _view_copy_guard(
                        item, _depth + 1, seen,
                        _path + "[" + str(index) + "]", _walked,
                        _act, _argument)
        finally:
            seen.discard(id(value))
        _walked.add((id(value), _depth))


def _guard_context(act, argument):
    """The act and argument clause of a guard refusal: the act
    that refused and the argument it refused, stated in the
    refusal itself, or no clause where no act stands named."""
    if act is None:
        return ""
    if argument is None:
        return ": " + act + " refused the handed value"
    return ": " + act + " refused the " + argument + " argument"


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
        _view_copy_guard(
            record, _act="select_view_records",
            _argument="record at position " + str(index))
        selected.append(_guarded_copy(record))
    return selected


def _first_barred_field(value, _seen=None):
    """Return the first barred field name a value carries, judged
    on the keys of the records it holds, in the order those keys
    and parts stand handed, or None where it carries none. A
    container part stands searched through its base entries, and
    a part already searched on this walk stands not searched
    again, so a shared or cyclic part cannot loop the search."""
    if _seen is None:
        _seen = set()
    if isinstance(value, dict):
        if id(value) in _seen:
            return None
        _seen.add(id(value))
        for key, item in dict.items(value):
            if _is_barred_key(key):
                return key
            found = _first_barred_field(item, _seen)
            if found is not None:
                return found
            if isinstance(key, (dict, list, tuple, set, frozenset)):
                found = _first_barred_field(key, _seen)
                if found is not None:
                    return found
        return None
    if isinstance(value, (list, tuple, set, frozenset)):
        if id(value) in _seen:
            return None
        _seen.add(id(value))
        entries = _base_entries(value)
        if isinstance(value, (set, frozenset)):
            entries = sorted(entries, key=repr)
        for index, item in entries:
            found = _first_barred_field(item, _seen)
            if found is not None:
                return found
        return None
    return None


def _barred_field_label(field):
    """Return the name a barred field stands refused under: its
    stored text where it carries text, its base representation
    where it carries none."""
    text = _stored_text(field)
    if text:
        return text
    return repr(field)


def _barred_group_and_field(record):
    """Return the input group and the barred field a built view
    record carries, searching the contents group, the reputation
    and band group, and the graph position group in that order,
    then every remaining group of the record under its own field
    name, or None where the record carries no barred field."""
    groups = [
        ("contents", dict.get(record, "view_contents")),
        ("reputation_and_band",
         dict.get(record, "reputation_and_band_values")),
        ("graph_position",
         dict.get(record, "graph_position_as_seen")),
    ]
    for group, value in groups:
        field = _first_barred_field(value)
        if field is not None:
            return group, field
    for key, item in dict.items(record):
        if _is_barred_key(key):
            return _barred_field_label(key), key
        field = _first_barred_field(item)
        if field is not None:
            return _barred_field_label(key), field
    return None


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
    _view_copy_guard(contents, _act="build_view_record", _argument="contents")
    _view_copy_guard(reputation_and_band or {}, _act="build_view_record", _argument="reputation_and_band")
    _view_copy_guard(graph_position or {}, _act="build_view_record", _argument="graph_position")
    stated_position = position
    if stated_position is None and isinstance(run_record, dict):
        stated_position = dict.get(
            run_record, "scheduling_position_identifier")
        if stated_position is None:
            stated_position = dict.get(run_record, "position")
        if stated_position is None:
            by_day = dict.get(run_record, "positions_by_day")
            if isinstance(by_day, dict):
                if dict.__contains__(by_day, str(day)):
                    stated_position = dict.get(by_day, str(day))
                else:
                    stated_position = dict.get(by_day, day)
    memo = {}
    first_seen = {}
    delays = {}
    derived = bool(contents)
    for index, item in enumerate(contents):
        seen_day = None
        applied = None
        if isinstance(item, dict):
            if dict.__contains__(item, "first_seen_day"):
                seen_day = dict.get(item, "first_seen_day")
            else:
                seen_day = dict.get(item, "day")
            if dict.__contains__(item, "delay"):
                applied = dict.get(item, "delay")
            else:
                applied = dict.get(item, "delay_applied")
        first_seen[str(index)] = _freeze(seen_day, memo)
        delays[str(index)] = _freeze(applied, memo)
        if seen_day is None or applied is None:
            derived = False
    record = {
        "run_identifier": run_id,
        "viewer_identifier": viewer_id,
        "simulated_day": day,
        "scheduling_position_identifier": _freeze(stated_position, memo),
        "rule_version_set": _freeze(rule_version_set, memo),
        "view_contents": [_freeze(item, memo) for item in contents],
        "reputation_and_band_values": _freeze(reputation_and_band or {}, memo),
        "graph_position_as_seen": _freeze(graph_position or {}, memo),
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
        located = _barred_group_and_field(record)
        if located is not None:
            group, field = located
            raise NamedFailure(
                "build_view_record refused a barred field: the "
                + group + " group carries the barred field "
                + _barred_field_label(field)
                + ", and no view record stands written"
            )
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
            if _is_barred_key(node) and not any(
                    _is_barred_key(key) for key in dict.keys(node)):
                return True
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
    _view_copy_guard(view_record, _act="hold_view", _argument="view_record")
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

    view_record = dict.get(held, "view_record") if isinstance(held, dict) else None
    try:
        check = mod10.run_view_leak_check(view_record)
    except ValueError as exc:
        raise NamedFailure(str(exc)) from exc
    released = _guarded_copy(held)
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
    beside the manifest. The run identifier and the day stand
    read from the stored contents of the manifest through base
    dict operations, never through a get reading the handed
    manifest itself supplies. Every state part, the clock value
    among them, stands frozen through the guarded copy under
    one shared memo, and the paired manifest carries the
    assembled state itself, with no second copy of it taken by
    any copy protocol. The assembled pair stands guarded as one
    value before validation and retention, so a state part
    standing too deep in the pair the act builds meets the one
    guard refusal form at every depth, and no deeper act states
    a different cause for it."""
    from crucible import mod01, mod10

    _view_copy_guard(manifest, _act="write_checkpoint", _argument="manifest")
    _view_copy_guard(agent_states, _act="write_checkpoint", _argument="agent_states")
    _view_copy_guard(escrow_contract_states, _act="write_checkpoint", _argument="escrow_contract_states")
    _view_copy_guard(detection_state, _act="write_checkpoint", _argument="detection_state")
    _view_copy_guard(stream_positions_and_generator_states, _act="write_checkpoint", _argument="stream_positions_and_generator_states")
    _view_copy_guard(simulation_clock_value, _act="write_checkpoint", _argument="simulation_clock_value")
    if not isinstance(manifest, dict):
        raise NamedFailure(
            "checkpoint writing in named form: a checkpoint stands "
            "on a manifest record, and no other form stands written")
    run_id = dict.get(manifest, "run_identifier") or dict.get(manifest, "run_id")
    day = dict.get(manifest, "simulated_day")
    if run_id is None or day is None:
        raise NamedFailure(
            "checkpoint writing in named form: no run identifier or "
            "no simulated day stands on the manifest, and no "
            "checkpoint stands written under no identity")
    memo = {}
    state = {
        "run_identifier": run_id,
        "simulated_day": day,
        "agent_states": _freeze(agent_states, memo),
        "escrow_contract_states": _freeze(escrow_contract_states, memo),
        "detection_state": _freeze(detection_state, memo),
        "stream_positions_and_generator_states": _freeze(
            stream_positions_and_generator_states, memo),
        "simulation_clock_value": _freeze(simulation_clock_value, memo),
    }
    paired = _freeze(manifest, memo)
    paired["checkpoint_state"] = state
    _view_copy_guard(
        paired, _act="write_checkpoint",
        _argument="assembled checkpoint pair")
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
    mod10.retain_checkpoint(paired)
    return {"manifest": paired, "checkpoint_state": state}


def per_viewer_components(run_id="run-under-test", viewers=None, components=None):
    """The per viewer components of one run: every component
    carries its viewer identifier, and no component stands as a
    singular vector. Where components stand handed in, they stand
    returned per viewer in the order given."""
    if components is not None:
        memo = {}
        copied = []
        for position, item in enumerate(components):
            _view_copy_guard(
                item, _act="per_viewer_components",
                _argument="component at position " + str(position))
            copied.append(_freeze(item, memo))
        return copied
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

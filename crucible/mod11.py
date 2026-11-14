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
import re

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


def retirement_verdicts(fixture):
    """Return the per check verdicts of the retirement test for a
    fixture, over all fifteen checks T-01 to T-15 in the version of
    the report format paper pinned in the family record."""
    if fixture == "F-01":
        return dict(_F01_VERDICTS)
    if fixture in ("F-02", "EX-01"):
        return dict(_EX01_VERDICTS)
    raise ValueError("no retirement verdict stands recorded for: " + str(fixture))


def retirement_tally(fixture):
    """Return the retirement tally of one fixture as its own
    record. The F-01 tally and the EX-01 tally stand apart and
    stand never merged."""
    tally = _tally(retirement_verdicts(fixture))
    tally["fixture"] = fixture
    if fixture == "F-01":
        tally["centre_quarantine_breach"] = True
    return tally


def validate_publication_record(record):
    """Return True only for a complete publication record: it
    names the retirement test run that covered the unit, the
    version that run used, the verdict on each of the fifteen
    checks, and every failure that run recorded."""
    if not isinstance(record, dict):
        return False
    if not record.get("test_run") or not record.get("version"):
        return False
    verdicts = record.get("verdicts")
    if not isinstance(verdicts, dict):
        return False
    if tuple(sorted(verdicts)) != tuple(sorted(RETIREMENT_CHECKS)):
        return False
    recorded_failures = list(record.get("failures_recorded") or [])
    expected = [
        check for check in RETIREMENT_CHECKS
        if verdicts.get(check) == "failed"
    ]
    return recorded_failures == expected


def unit_is_publishable(unit):
    """Return True only where a unit carries a valid publication
    record. A unit covered by no recorded test run, or by a run
    with an unrecorded failure, is not published."""
    if not isinstance(unit, dict):
        return False
    return validate_publication_record(unit.get("publication_record"))


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
    judgements and a checker who did not compile the entry."""
    same_person = compiler == checker
    phases = (entry or {}).get("phase_judgements") or {}
    judged = {
        "before_runs": phases.get("before_runs") == "judged",
        "after_runs": phases.get("after_runs") == "judged",
    }
    comparison = None
    if not same_person:
        comparison = mod13.compare_registry_against_run_log(
            entry if isinstance(entry, dict) else {}, run_log=run_log)
    performed = bool(comparison and comparison["performed"])
    passed = bool(comparison and comparison["passed"])
    return {
        "before_runs_judged_for": "lateness",
        "after_runs_judged_for": "completeness",
        "phases_judged": judged,
        "compared_against_run_log": performed,
        "registry_comparison": comparison,
        "checker_did_not_compile": not same_person,
        "valid": (not same_person) and all(judged.values())
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
    field beyond the fourteen, quotable whole or not at all."""
    if not isinstance(values, dict):
        raise ValueError("a headline unit is built from a field mapping")
    extra = [key for key in values if key not in HEADLINE_UNIT_FIELDS]
    if extra:
        raise ValueError("fields beyond the closed unit: " + ", ".join(extra))
    unit = {}
    for field in HEADLINE_UNIT_FIELDS:
        if field not in values or values[field] is None:
            raise ValueError("headline unit field absent: " + field)
        unit[field] = copy.deepcopy(values[field])
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


def _part_text(value, _depth=0):
    """Return the text a unit part carries, read through base
    class readings only, so a string form stands beside a block
    form of the same part."""
    if _depth > _DEPTH_BOUND and isinstance(
            value, (dict, list, tuple, set, frozenset)):
        return ""
    if isinstance(value, str):
        return str.__str__(value)
    if isinstance(value, dict):
        parts = []
        for key, item in dict.items(value):
            parts.append(str(key))
            parts.append(_part_text(item, _depth + 1))
        return " ".join(parts)
    if isinstance(value, (list, tuple, set, frozenset)):
        return " ".join(
            _part_text(item, _depth + 1) for item in _base_iter(value))
    if value is None:
        return ""
    return str(value)


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
    from a noun of the lexicon counts with that noun."""
    stems = []

    def undoubled(stem):
        if len(stem) > 2 and stem[-1] == stem[-2] \
                and stem[-1] not in _READABLE_VOWELS:
            return stem[:-1]
        return None

    if word.endswith("ies") and len(word) > 4:
        stems.append(word[:-3] + "y")
    if word.endswith("es") and len(word) > 3:
        stems.append(word[:-2])
    if word.endswith("s") and len(word) > 3:
        stems.append(word[:-1])
    if word.endswith("ed") and len(word) > 4:
        stems.append(word[:-2])
        stems.append(word[:-1])
        plain = undoubled(word[:-2])
        if plain is not None:
            stems.append(plain)
    if word.endswith("ing") and len(word) > 5:
        stems.append(word[:-3])
        stems.append(word[:-3] + "e")
        plain = undoubled(word[:-3])
        if plain is not None:
            stems.append(plain)
    if word.endswith("ly") and len(word) > 4:
        stems.append(word[:-2])
    if word.endswith("er") and len(word) > 4:
        stems.append(word[:-2])
    if word.endswith("est") and len(word) > 5:
        stems.append(word[:-3])
        stems.append(word[:-2])
        plain = undoubled(word[:-3])
        if plain is not None:
            stems.append(plain)
    if word.endswith("y") and len(word) > 4:
        stems.append(word[:-1])
        stems.append(word[:-1] + "e")
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
    each stand in the lexicon in plain form; a compound with
    a part outside the lexicon counts as no word."""
    if len(word) < 3:
        return False
    if word in _READABLE_LEXICON:
        return True
    if any(stem in _READABLE_LEXICON
           for stem in _readable_stem(word)):
        return True
    for split in range(3, len(word) - 2):
        if word[:split] in _READABLE_LEXICON \
                and word[split:] in _READABLE_LEXICON:
            return True
    return False


def _plain_word_count(text):
    """Count plain words on the readable word reading: each
    distinct readable word in the text counts once, so a sentence
    repeating one word counts that word once, and a letter string
    that stands as no readable word counts not at all."""
    words = re.findall(r"[A-Za-z]+", str(text).lower())
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
    the forms that state the number after the q."""
    tokens = _ground_tokens(other)
    grounds = set()
    ordinal_numbers = {
        "first": "1", "second": "2", "fifth": "5",
        "1st": "1", "2nd": "2", "5th": "5",
    }
    for index, token in enumerate(tokens):
        if token in ordinal_numbers:
            window = tokens[max(0, index - 3):index + 4]
            if "parley" in window and any(
                    word in ("question", "questions")
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
    if tuple(dict.keys(unit)) != HEADLINE_UNIT_FIELDS:
        return False
    identifier = dict.get(unit, "headline_unit_identifier_and_issue_date")
    if isinstance(identifier, str):
        identifier = str.__str__(identifier)
    else:
        identifier = str(identifier)
    if F01_UNIT_MARK in identifier:
        return False
    for field in HEADLINE_UNIT_FIELDS:
        if dict.get(unit, field) is None:
            return False
        if not _envelope_part_stands(dict.get(unit, field)):
            return False
    for field in ("holding_region", "failure_region"):
        if not _region_stands(dict.get(unit, field)):
            return False
    claim = dict.get(unit, "claim_sentence")
    if isinstance(claim, str):
        claim = str.__str__(claim)
    claim = str(claim).lower()
    if "everywhere" in claim or "all points" in claim:
        return False
    if not _field10_stands(
            dict.get(unit, "qualifiers_and_markings_block")):
        return False
    if not _field10_matches_grounds(unit):
        return False
    if not _has_plain_scope_limits_sentence(
            dict.get(unit, "claim_sentence")):
        return False
    if not _has_plain_scope_limits_sentence(
            dict.get(unit, "grounding_sentence")):
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
    part itself is ever invoked. A value nested past the depth
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
        return value.tobytes()
    if isinstance(value, dict):
        if id(value) in _memo:
            return _memo[id(value)]
        copied = {}
        _memo[id(value)] = copied
        for key, item in dict.items(value):
            copied[_quoted_copy(key, _memo, _depth + 1)] = _quoted_copy(
                item, _memo, _depth + 1)
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
            for item in set.__iter__(value):
                copied.add(_quoted_copy(item, _memo, _depth + 1))
            return copied
        copied = frozenset(
            _quoted_copy(item, _memo, _depth + 1)
            for item in frozenset.__iter__(value))
        if id(value) in _memo:
            return _memo[id(value)]
        _memo[id(value)] = copied
        return copied
    if isinstance(value, (str, bytes, bytearray, int, float, complex,
                          bool)) or value is None:
        return value
    return value


def quote_headline_unit(unit):
    """Quote a headline unit whole. A unit that does not validate
    is not quoted at all. The quotation copies the validated unit
    through base class readings only, never through a copy
    protocol a part of the unit overrides. A standing memoryview
    part stands quoted as the bytes content it carries, so
    quotation of a standing unit never fails in the copy act
    itself."""
    if not validate_headline_unit(unit):
        raise ValueError("a headline unit is quotable whole or not at all")
    return _quoted_copy(unit)


def first_sentence(text):
    """Return the first sentence of a claim text."""
    return str(text).split(".", 1)[0]


def validate_working_range_claim(text, assumption_set, rows, range_kind):
    """Return True only where the first sentence of a working
    range claim names its assumption set, its rows, and its range
    kind. A first sentence naming none of the three, or only some
    of them, does not meet the claim form."""
    sentence = first_sentence(text)
    if _is_code_only_text(sentence):
        return False
    return all(
        str(named) in sentence
        for named in (assumption_set, rows, range_kind)
    )


def moved_reading(delta, reporting_resolution):
    """Decide moved or not moved for one trace: the trace moved
    where its change reaches the reporting resolution for that
    trace stated in the family record before runs. The rule reads
    only the recorded change and the recorded resolution, so a
    second reader applying it to the same record reaches the same
    reading."""
    return abs(delta) >= reporting_resolution


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
    if tuple(headline.get("axes") or ()) != AXES:
        return False
    traces = headline.get("traces") or []
    if len(traces) != 3:
        return False
    for trace in traces:
        if not isinstance(trace, dict) or "moved" not in trace:
            return False
    needs_witness = headline.get("rests_on_axis") == "external work issuance"
    edge_count = (run_record or {}).get("farm_internal_edge_count")
    bound = (family_record or {}).get("near_zero_bound")
    if edge_count is not None and bound is not None and edge_count <= bound:
        needs_witness = True
    if needs_witness and not headline.get("zero_edge_witness_shape"):
        return False
    return True


def validate_envelope_claim(claim):
    """Return True only under envelope discipline: the claim
    states what holds at sampled points and over the stated ranges
    only, names a failure witness for what fails, and states
    nothing about values between sampled points."""
    if not isinstance(claim, dict):
        return False
    if "holding_region" in claim or "claim_sentence" in claim:
        if not validate_headline_unit(claim):
            return False
        if claim.get("failure_region") and not _region_stands(
                claim.get("witness_block")):
            return False
        return True
    if claim.get("scope") != "sampled points and stated ranges only":
        return False
    if claim.get("claims_between_points"):
        return False
    if claim.get("monotonicity_claimed") or claim.get("interpolation_claimed"):
        return False
    if claim.get("holds") is False and not claim.get("failure_witness"):
        return False
    return True


def honest_loss_rate_h1(submitted, accepted_by_submission_period):
    """The honest loss rate in the decided H1 form: the period
    subtraction, with each accepted unit attributed to the period
    in which it was submitted. So attributed, the subtraction
    equals the event count by construction and cannot fall below
    zero. The rate travels as a stored numerator and denominator
    pair."""
    numerator = int(submitted) - int(accepted_by_submission_period)
    if numerator < 0:
        numerator = 0
    return {
        "form": "H1",
        "numerator": numerator,
        "denominator": int(submitted),
    }


def top_up_applies(winning_probability):
    """The top up duty at F-18, read with closed bounds: it
    applies at or above 0.1 and at or below 0.9."""
    return 0.1 <= winning_probability <= 0.9


def point_standing(replicate_count):
    """Return the standing of one control point against the 30
    replicate floor, with its count stated. A point below the
    floor borrows no standing of a point at the floor."""
    count = int(replicate_count)
    return {
        "replicates": count,
        "standing": "at floor" if count >= 30 else "below floor",
    }


def classify_run_outcome(run_length_in_days, regime_class):
    """Classify one run outcome. A run shorter than 30 simulated
    days is not classifiable as attacker winning under the final
    30 day rule: its outcome stands recorded as horizon
    insufficient and contributes to no transition figure."""
    if int(run_length_in_days) < 30:
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
    never as censoring. The denominator rule stands stated in the
    result."""
    total = len(replicates)
    counts = {}
    competing = 0
    censored = 0
    for replicate in replicates:
        if replicate.get("competing_exit"):
            competing += 1
            continue
        regime = replicate.get("first_terminal_regime")
        if regime is None:
            censored += 1
        else:
            counts[regime] = counts.get(regime, 0) + 1
    denominator = total if total else 1
    incidence = {
        regime: {"count": count, "denominator": total,
                 "share": count / denominator}
        for regime, count in counts.items()
    }
    return {
        "denominator": total,
        "denominator_rule": (
            "computed over all replicates started at the point; "
            "competing regime exits counted as competing events "
            "and never as censoring"),
        "cumulative_incidence": incidence,
        "competing_events": competing,
        "right_censored": {
            "count": censored, "denominator": total,
            "share": censored / denominator,
        },
        "outcomes_per_replicate": 1,
    }


def location_for_endpoint(figure, regime, band_endpoint):
    """Return the location of a band endpoint at a point, or None
    where cumulative incidence by the horizon does not reach the
    endpoint: no location stands reported for that endpoint at
    that point."""
    entry = (figure.get("cumulative_incidence") or {}).get(regime)
    if entry is None or entry["share"] < band_endpoint:
        return None
    return {"regime": regime, "endpoint": band_endpoint,
            "share": entry["share"]}


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
    if record.get("exact_event_time") is not None:
        return False
    interval = record.get("interval")
    return isinstance(interval, (list, tuple)) and len(interval) == 2


def region_shift_steps(location_a, location_b):
    """Return the shift of a region location between two points,
    in grid steps on each axis."""
    return (
        abs(int(location_a[0]) - int(location_b[0])),
        abs(int(location_a[1]) - int(location_b[1])),
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
    shift = region_shift_steps(location_a, location_b)
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
    if not report.get("distribution_near_threshold"):
        return False
    counts = report.get("regime_class_counts") or {}
    if len(counts) != 3:
        return False
    rate = report.get("honest_loss_rate") or {}
    if rate.get("form") != "H1":
        return False
    for point in report.get("points") or []:
        if point.get("near_threshold") and int(point.get("replicates", 0)) < 30:
            return False
        probability = point.get("winning_probability")
        if probability is not None and top_up_applies(probability):
            if not point.get("top_up_recorded"):
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
    figure = unit.get("transition_figure") or {}
    if not figure.get("cumulative_incidence"):
        return False
    if "right_censored" not in figure:
        return False
    if unit.get("incidence_label") != "derived from the replicate counts in this unit":
        return False
    horizon = unit.get("horizon")
    if horizon is None:
        horizon = figure.get("horizon")
    if horizon is None:
        horizon = figure.get("stated_horizon")
    if horizon is None:
        horizon = unit.get("stated_horizon")
    for sentence in unit.get("location_sentences") or []:
        if not isinstance(sentence, str) or "horizon" not in sentence:
            return False
        numbers = re.findall(r"[0-9]+(?:\.[0-9]+)?", sentence)
        if not numbers:
            return False
        if horizon is not None:
            lowered = sentence.lower()
            positioned = re.findall(
                r"([0-9]+(?:\.[0-9]+)?)\s*(?:days?\s+)?horizon",
                lowered)
            positioned += re.findall(
                r"horizon\s*(?:is\s+|of\s+|:|=)?\s*"
                r"([0-9]+(?:\.[0-9]+)?)",
                lowered)
            if not positioned:
                return False
            if not any(float(value) == float(horizon)
                       for value in positioned):
                return False
    return True


def reporter_inputs_for_family(retained_records):
    """Return the Reporter inputs of one family as carried through
    the retained records at S-10: the divergence count computed at
    S-04 as it stands, or the blocked family mark where it stands,
    naming the affected family and the affected share."""
    records = retained_records or {}
    return {
        "divergence_count": records.get("divergence_count"),
        "blocked_family_mark": copy.deepcopy(
            records.get("blocked_family_mark")),
    }


def share_report_stands(inputs, share):
    """Report whether a report may read an affected share as
    standing as reported. The function returns a boolean only: it
    reports the standing of the share for reading, and no caller
    wires it into the headline unit build path. While a blocked
    family mark stands for a share, with its count nonzero and
    unresolved, the function returns False for that share, and it
    returns True otherwise."""
    mark = (inputs or {}).get("blocked_family_mark")
    if isinstance(mark, dict) and mark.get("affected_share") == share:
        if mark.get("count", 0) and not mark.get("resolved"):
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
                copy.deepcopy(failure))
        return {"built": False, "failure": failure, "unit": None}
    except Exception as error:
        failure = {
            "name": type(error).__name__ + ": " + str(error),
            "run_status": "failed",
            "complete": False,
            "run_identifier": run_id,
        }
        if isinstance(family_record, dict):
            family_record.setdefault("named_failures", []).append(
                copy.deepcopy(failure))
        return {"built": False, "failure": failure, "unit": None}
    unit_values = dict(values)
    unit_values.setdefault(
        "run_registry_line",
        "run record " + str(run_id) + " read in one lookup")
    provenance = {
        "record": run_id,
        "record_state": record.get("record_state", "as retained"),
        "inside_unit": True,
    }
    unit_values["checkability_fields"] = provenance
    unit = make_headline_unit(unit_values)
    return {"built": True, "failure": None, "unit": unit}


def weekly_count(summary_records, week):
    """Compute the weekly headline reading load from the stored
    summary records alone: distinct headline unit identifiers
    whose witness records fall in the week, one unit counting
    once however many runs support it."""
    identifiers = set()
    for record in summary_records or []:
        if not isinstance(record, dict) or "week" not in record or "headline_unit_identifiers" not in record:
            raise ValueError("weekly count stands refused in named form: a summary record carries no week or no headline unit identifiers, and no silent zero stands counted")
        if record.get("week") != week:
            continue
        for identifier in record.get("headline_unit_identifiers") or []:
            identifiers.add(identifier)
    return len(identifiers)


_UNIT_IDENTIFIER_PATTERN = re.compile(r"u[0-9]+")


def _unit_identifier_stands(item):
    """Return True only where an item stands as one headline unit
    identifier in the standing form the weekly pins use: the
    letter u followed by one or more plain digits, and nothing
    else."""
    return isinstance(item, str) and \
        _UNIT_IDENTIFIER_PATTERN.fullmatch(item) is not None


def make_weekly_container(week, units):
    """Build the weekly container for one week in arrival order.
    At most 25 whole headline units stand in the container under
    decision D-12. A unit beyond the cap stands held, reported as
    held in the container record of its own week. Each held item
    stands validated against the standing unit identifier form
    before any count stands taken, and an item that does not
    stand in that form stands refused in named form, so no count
    stands stated over unvalidated contents."""
    ordered = list(units or [])
    for item in ordered:
        if not _unit_identifier_stands(item):
            raise ValueError(
                "weekly container stands refused in named form: "
                "a held item stands in no unit identifier form, "
                "and no count stands taken over unvalidated "
                "contents: " + repr(item))
    inside = ordered[:WEEKLY_CAP]
    held = ordered[WEEKLY_CAP:]
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
    released = list((previous_container or {}).get("held_units") or [])
    return make_weekly_container(week, released + list(new_units or []))


def claim_enters_family(family_record, claim, results_seen):
    """Return True only where a claim may enter a family: the
    family stands fixed before runs, and no claim enters the
    family after results are seen."""
    if results_seen:
        return False
    return claim in ((family_record or {}).get("headline_claims") or [])


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
    quantities = readout.get("quantities")
    if not isinstance(quantities, (list, tuple)) or not quantities:
        return False
    for quantity in quantities:
        if not isinstance(quantity, dict):
            return False
        name = quantity.get("name")
        if not isinstance(name, str) or len(name.strip()) < 2 \
                or _plain_word_count(name) < 1:
            return False
        number = quantity.get("recorded_number")
        if isinstance(number, bool) or not isinstance(number, (int, float)):
            return False
        if quantity.get("class_based"):
            rule = quantity.get("class_rule")
            if not isinstance(rule, str) or not rule.strip():
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
    entries = form.get("entries")
    if not isinstance(entries, (list, tuple)) or not entries:
        return False
    for entry in entries:
        if not isinstance(entry, dict):
            return False
        keys = tuple(entry.keys())
        if keys not in (("row", "column", "quantity"),
                        ("row", "period", "quantity")):
            return False
        for identifier in (entry["row"], entry[keys[1]]):
            if identifier is None or (isinstance(identifier, str)
                                      and not identifier.strip()):
                return False
        quantity = entry["quantity"]
        if isinstance(quantity, bool) or not isinstance(
                quantity, (int, float)):
            return False
    return True


def validate_family_record(family_record):
    """Return whether a family record passes MOD-01 validation
    for Form 1 and supports a reportable run under its
    completeness bar."""
    if not isinstance(family_record, dict):
        return False
    if not mod01.validate_record("1", family_record):
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

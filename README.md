# Crucible

Crucible is a Monte Carlo agent society simulator. Its design simulates hundreds of agents trading, vouching, and defecting across extended runs, with trust rules, escrow, and detection inside the simulation, to measure the conditions under which bad actors start winning.

Status: in development, no release yet. The Python package described below stands importable and usable today for the record, validation, and store surfaces this page names. The package does not run a simulation today: executable runs stand gated, as the gate section below states.

## What the package offers today

Today the package offers the record forms of the design as checkable Python records, validation of those records, a recorder store that retains and reads back run records, checkpoint and snapshot retention, and the reporting and checking surfaces that read retained records. It offers no command line interface and no executable simulation run.

## How to import it

The interface is the Python package itself. With the package directory on the Python path:

```python
import crucible
from crucible import mod01

record = mod01.minimal_valid_instance("2")
stands = mod01.validate_record("2", record)
```

Each module also stands imported by its own path, for example `from crucible import mod10` for the recorder store.

## Where the forms live

The record forms live in mod01, Types and validation. `crucible.mod01.FORM_TYPES` maps each form identifier to its named form class, `form_fields` and `required_fields` state the fields of a form, and `minimal_valid_instance` returns a formally complete template of a form as a plain dict. At Form 1 the template carries the six completeness fields under their spaced brief spellings beside the Form 1 field names: those spaced keys stand as aliases of the fields the form names, the stated alias exception at Form 1, and a record carrying a completeness field under its spaced spelling stands within its form at validation. Named construction guidance stands at `build_sweep_point` for Form 2 and `build_run_record` for Form 4, with field ownership stated in `FORM_FIELD_OWNERSHIP`: which fields a user supplies, which fields the system fills, and which fields, the seed fields on Form 4, a user must never fill.

## Record forms: brief Shape and product Form numbering

The design brief numbers its record shapes (brief Shapes 1 to 17), and the product numbers its record forms (product Forms 1 to 37 and Form 13A). The two numberings agree up to Shape 8. Brief Shape 8 states two forms, VouchEdge and GraphSnapshot, so from brief Shape 9 onward the product Form number runs one ahead of the brief Shape number. Read a brief Shape through this table, or through `BRIEF_SHAPE_CROSS_REFERENCE`, `brief_shape_for_form`, and `form_ids_for_brief_shape` in `crucible.mod01`, never by assuming the two numbers agree.

| Brief Shape | Product Form | Record |
|---|---|---|
| Shape 1 | Form 1 | SweepFamilyRecord |
| Shape 2 | Form 2 | SweepPoint |
| Shape 3 | Form 3 | AssumptionRecord |
| Shape 4 | Form 4 | RunRecord |
| Shape 5 | Form 5 | SeedDerivationInput |
| Shape 6 | Form 6 | StreamSet |
| Shape 7 | Form 7 | AgentState |
| Shape 8, first form | Form 8 | VouchEdge |
| Shape 8, second form | Form 9 | GraphSnapshot |
| Shape 9 | Form 10 | EscrowContractState |
| Shape 10 | Form 11 | AdjudicationCase |
| Shape 11 | Form 12 | DetectionState |
| Shape 12 | Form 13 | CheckpointManifest |
| Shape 13 | Form 14 | DailyAggregates |
| Shape 14 | Form 15 | JointOutcomeVector |
| Shape 15 | Form 16 | HeadlineResultUnit |
| Shape 16 | Form 17 | AnchorScenarioRecord |
| Shape 17 | Form 18 | InterpretationLogEntry |

The Form 5 record and the derivation input stand as different shapes. The record form table above names Form 5 as the SeedDerivationInput record of mod01, and mod02 states its derivation input under its own field names: a Form 5 record carries derivation_version_string where the derivation input carries derivation_version, and recorded_root_seed where the derivation input carries root_seed_reference; the remaining fields, domain, scenario_identifier, run_identifier, stream_class_identifier, and parameter_values, carry the same names in both shapes. A Form 5 record therefore stands not handed to mod02.derive_seed as it stands: build the derivation input in the derivation act field names, through mod02.make_derivation_input, and hand that value in.

Forms carrying no numbered brief Shape of their own: Form 13A (CheckpointState) stands beside Form 13 in the checkpoint layer; Form 19 (DetectionInput) stands defined inside the Shape 7 passage; Forms 20 and 21 (AnnotationRecord and AnnotationCheckRecord) stand defined in the Shape 16 passage; Forms 22 to 37 are layer three forms with no numbered brief Shape.

## The DQ7-02 gate

Executable runs stand gated on DQ7-02. No adoption record for the DQ7-02 gate stands, so no seed can be derived and no run can start: seed derivation, run starting, and the tick engine each refuse in named form, stating the gate, the ground, and that nothing stands for the operator to do. The record, validation, store, and reading surfaces above stand open and ungated.

## Surface guide

The package carries fifteen modules, mod01 to mod14 and mod16, exporting 660 names in total on the summed basis, the sum of the fifteen module export lists. On validation, the guide states the pair plainly: validate_record answers True or False, and record_validation_failures in the same module states the reasons for a failing validation.

| Module | Purpose |
|---|---|
| mod01 | Types and validation: every record form, its fields, and the validation acts |
| mod02 | Seed and Stream Engine: the seed derivation and stream interface, gated as above |
| mod03 | Society Generator: archetype generators and cast construction |
| mod04 | Tick Engine: the run engine, DetectionInput projection, and view edges, gated as above |
| mod05 | Parley Core: work credit, vouching, and reputation aggregation in comparison form |
| mod06 | Escrow Core: the escrow contract cores |
| mod07 | Escrow Adapter: the adapter and seam records between the cores |
| mod08 | Detection Layer: Vigil style scoring inside a run |
| mod09 | Attacker Seat: attacker strategies and the search ladder |
| mod10 | Recorder and stores: retention, stores, checkpoints, and reading paths |
| mod11 | Reporter: headline result units and the family registry reading path |
| mod12 | Sweep Controller: sweep family definition, the seal path, and run starting, gated as above |
| mod13 | Replication Checker: replay checks and the scoring interface |
| mod14 | Shell: pilot runner and program checks |
| mod16 | Integration surface: fixtures and validation runs composing the modules above |

### User entry points

The intended user entry points stand as: `mod01.validate_record`, `mod01.record_validation_failures` (the act that states the reasons for a failing validation, naming each field, its ground, and its next step, so a False from validate_record stands followed to its ground), `mod01.minimal_valid_instance`, `mod01.minimal_valid_family_record`, `mod01.build_sweep_point`, `mod01.build_run_record`, and the `FORM_TYPES` classes for records; `mod10.new_store`, `mod10.retain_run_record`, and `mod10.read_run_record` for the store; and the refusal returning acts of mod12 for any attempt to start a run. The top level package re-exports the mod01 surface.

### Internal surface

The Internal surface stands as: every name beginning with an underscore in any module, which stands private by convention and carries no user promise; the helper machinery behind the entry points, including traversal guards, stored form renderings, and segmentation helpers in mod10; and the module level stores and registries a module states as its own working state. A user builds on the entry points above and treats the rest as internal.

## License

Apache License 2.0. Copyright 2026 J.P. Picard aka Macro-Harder.

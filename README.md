# Crucible

A Monte Carlo agent society simulator that stress tests a trust stack at scale. Hundreds of simulated agents trade, vouch, and defect over simulated years while trust rules, escrow, and detection run inside the simulation, so the conditions under which bad actors start winning can be measured instead of guessed.

Status: build in progress. The system lands here as it is built, one verified piece at a time. Design records live in a separate private repo and are not part of this repo.

License: Apache License 2.0. Copyright 2026 J.P. Picard aka Macro-Harder.

## Install procedure

The product ships as one versioned release archive, built from the recorded head of this repo. The archive contains the product source in full, the example inputs that travel with the product as fixtures, the licence file, and the final build document. One manifest inside the archive lists every file it contains with its hash. No second distribution form ships, and no dependency outside the archive is required at install time beyond the host environment stated here: a Python 3 interpreter, standard library only.

Install in this order:

1. Obtain the release archive and record its identity before installing: the version in three part numeric form, the source commit of this repo the release was built from, and the tree hash of that commit.
2. Unpack the archive into the install location on the target host.
3. Verify the install file by file: hash every installed file and compare each hash against the archive manifest, then compare the manifest against the recorded head the archive was built from. An install whose files do not match the manifest does not stand as installed.
4. Run the deterministic configuration check on the target: read the settings and environment values that deterministic mode requires, as the final build document lists them, and record each value read beside the value required. An install with any such setting absent, or with any value different from the required value, stands recorded as failed in the same form as a hash check failure, and no later step may cite that install as a conforming install until a fresh check passes.
5. Initialise the three stores the product keeps apart: the sweep store, the pilot store, and the live store. Each store is initialised as an empty store of its own kind, with no shared index between them, and pilot artefacts are stored apart from sweep results from the first write.
6. Record the form and the source of the first family record and of the assumption inputs, before any run. The first family record enters as a family record in the form the product states, supplied by the operator, and assumption inputs enter as assumption records in their stated form.
7. Run the verification command for this repo from the product directory: `python3 -m unittest discover -s tests`. The install stands verified only where the suite result stands recorded as a result, never as an intention.

No seed is drawn and no run is started at install time while no adoption record stands.

Where verification fails, the install stands recorded as failed, the proof step does not open on it, and the failure is owned by the installer of the product and escalated as a readiness blocker. The register entry for a failed first install states the target end state in one of two named forms, failed version present and unproven, or target uninstalled, and states beside it the verification result that proves that end state. The register entry for a failed reinstall states the target end state in one of three named forms, prior version restored, failed version present and unproven, or target uninstalled, with the proving verification result beside it. An entry stating neither the end state in one of those forms nor its proving result is incomplete and closes no install act.

## Operator runbook

The operator procedure for this product stands as the runbook in this section. It is the same procedure the shell surface carries in its runbook record; the shell owns no rule of its own and no result wording of its own, and every step below is a carriage or checking act, never a computation a core owns.

1. Read the family record and the run record before any act. The shell carries records and interprets none of them.
2. Start runs and sweeps through the start commands only. While the seed adoption record does not stand, every start returns the gated refusal that names its gate, and no run starts.
3. Keep pilot work inside its confinement: timing, conformance, and procedure rates only. Each pilot output carries its pilot confined label in the same artefact as its figure, and pilot artefacts are stored apart from sweep results.
4. Read stores by kind: sweep, pilot, and live. Never resolve a record across stores in one lookup.
5. Run the program checks by name: the store kind check; the flag evaluation, whose inputs and outcome stand written into the stored summary record itself; the weekly headline count, counted from the stored summary records alone; and the outside call check, computed from the dependency manifest and the process and network call log only, certifying only the absence the check reads.
6. Treat every named failure as the result of its act. Report it with its run identifier and its stage, and never present an empty result in its place, and never let a command exit cleanly over a failed run.
7. Make no edit to a sealed family record, to a closed run record outside the flag rule path, or to a checkpoint set outside the deletion rule. Validation reads checkpoint manifests beside the run record to compare seeds, settings, and rule versions.

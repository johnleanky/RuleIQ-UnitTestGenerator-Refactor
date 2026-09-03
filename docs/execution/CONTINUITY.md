# Project Continuity

This file is the single authoritative operational state for resuming repository work. Keep it concise and reconcile it with repository evidence at every checkpoint.

## Current State

- **Project objective:** Refactor the current monolithic Pega unit-test Author into a Scenario Author and a Unit Test Generator, with UUID-addressed Memory transport and Validator feedback, while preserving every stable instruction through explicit source-to-destination traceability and preserving schema-governed `UnitTestRules` output.
- **Repository root:** `C:/Dev/RuleIQ-UnitTestGenerator-Refactor/RuleIQ-UnitTestGenerator-Refactor`
- **Current branch:** `main`
- **Recorded HEAD:** `UNBORN` — the repository has no commit.
- **Remote tracking state:** `origin/main` is reported as gone.
- **Working-tree state:** `VERIFIED` — the unborn branch contains 20 untracked files: 16 pre-existing project files and four new documentation files; `AGENTS.md` remains untracked and was replaced in place.
- **Active stage:** None during the post-S0 baseline-commit checkpoint; `S0 — Baseline and Contract Stabilization` is closed and `S1` has not been selected as active.
- **Active ExecPlan:** [S0-baseline-contracts.md](plans/S0-baseline-contracts.md), closed and retained as the transition authority until the baseline commit is created and an S1 ExecPlan is selected.
- **Stage status:** `CLOSED` for S0; `NOT_STARTED` for S1.
- **Current project status:** `PARTIAL` — target architecture decisions are accepted, but no product refactor has started.

### Verified Completed Work

- `VERIFIED` — repository root, branch, unborn HEAD, remote tracking state, and initial untracked working tree were inspected on 2026-09-02.
- `VERIFIED` — no `AGENTS.override.md`, README, architecture, requirements, roadmap, ADR, plan, or task documents existed before continuity initialization.
- `VERIFIED` — the initial standard JSON example had an illegal trailing comma at line 269; this is retained as pre-fix evidence.
- `VERIFIED` — the accepted target architecture and continuity decisions are recorded in [DECISIONS.md](../decisions/DECISIONS.md).
- `VERIFIED` — the five continuity artifacts passed post-write path, link, language, stage, dependency, decision-field, next-action, and product-file-scope checks.
- `VERIFIED` — instruction-preservation and high-risk independent-validation requirements are accepted and recorded as durable decisions.
- `VERIFIED` — an independent read-only subagent reviewed the preservation and high-risk-gate additions on 2026-09-02 and returned `PASS` with no findings; the root agent reconciled the report against repository evidence.
- `VERIFIED` — the user authorized the root agent to create the initial baseline commit after S0 closure, confirmed that the new Pega exports do not exist and must be designed, selected `UnitTestGenerator` as the new agent rule name, and authorized the standard-example syntax repair and schema validation.
- `VERIFIED` — the 150-row Instruction Preservation Matrix passed independent review after all findings were corrected by the root agent on 2026-09-03.
- `VERIFIED` — the standard example comma defect is corrected; all four files parse, and both examples pass independently reviewed validation of every schema assertion keyword they use.
- `VERIFIED` — the 2026-09-03 restart checkpoint confirms unborn `main`, absent `HEAD`, gone `origin/main`, 20 untracked files, one active S0 stage, and one synchronized next action.
- `VERIFIED` — DEC-017 and affected stage language exclude `Main_Agent.txt` from parity, edits, and deliverables; after root correction of residual generic wording, independent follow-up review returned `PASS` on 2026-09-03.
- `VERIFIED` — the canonical `Main_Agent_Prompt.txt` baseline and decoded Validator prompt/export parity were recorded on 2026-09-03 without changing any product artifact.
- `VERIFIED` — the S1 entry-contract audit maps accepted interfaces and boundaries to evidence and records the user-confirmed opaque Payload/UUID contract as DEC-018; independent review confirmed it is sufficient to begin S1.
- `VERIFIED` — the first final S0 audit found three planning-document inconsistencies; the root corrected them, and focused independent follow-up returned `PASS` with no findings.
- `VERIFIED` — all mandatory S0 acceptance criteria are satisfied and S0 is closed as of 2026-09-03.
- `NOT_STARTED` — product prompt, schema, Pega export, and tool implementation changes.

### Blockers and Unknowns

- `UNKNOWN` — whether an installed full Draft 2020-12 validator or runnable Pega JsonValidationTool can reproduce the local schema-keyword validation; none is currently available without installing dependencies.
- `NOT_STARTED` — detailed Pega designs and exports for `WriteMemory`, `GetMemory`, UUID-aware `JsonValidationTool`, and `UnitTestGenerator`; their absence is planned implementation scope, not an external blocker.
- `IMPLEMENTED_NOT_VERIFIED` — the contract audit found no decision gap blocking S1. Pega storage metadata, response envelopes, UUID implementation, and exact failure codes are bounded S1 design work and may not weaken immutable exact addressing or opaque round trips.

### Validation State

- Continuity artifacts: `VERIFIED` by post-write re-read and structural checks on 2026-09-02.
- Standard schema JSON syntax: `VERIFIED` as parseable when decoded with UTF-8 BOM support.
- MultInpComb schema JSON syntax: `VERIFIED` as parseable when decoded with UTF-8 BOM support.
- Standard example JSON syntax: `VERIFIED`; line 269 is corrected and PowerShell, Python, and Node parsers pass after independent review.
- MultInpComb example JSON syntax: `VERIFIED` as parseable when decoded with UTF-8 BOM support.
- Schema conformance of examples: `VERIFIED` for every assertion keyword used by these schemas; independent Python and Node validators report zero errors for both families. Reproduction with a complete installed Draft 2020-12 package or Pega tool remains unavailable and is not claimed.
- Canonical Main prompt baseline: `VERIFIED`; `Main_Agent_Prompt.txt` has SHA-256 `D6CDED6A4D786AC555452C05296B1A409042B5E6853B0FB9B9EC635AF065C290`, 177,990 bytes, 2,219 logical lines, 1,710 non-empty lines, 66 Markdown headings, and six fence markers. It uses CRLF, has no UTF-8 BOM, and `Main_Agent.txt` was not read for parity or modified.
- In-scope Validator prompt/export semantic parity: `VERIFIED`; the export has exactly one `<pySystemPrompt>` boundary pair. After bounded HTML-fragment decoding, non-breaking-space and line-ending normalization, removal of empty lines, and trimming serializer-introduced boundary whitespace, both sides have 519 logical lines and SHA-256 `1B78FF5E6422BDE561A24704939D6185FCC7E70CF9806D76BBFBD55DB45B10AE`. The exact 3,137-token sequence also matches with SHA-256 `EA7F8BEB5141599F07A32519B0F4905AB3318524F1DE6AE4A0EF89999387DBC0`. A trailing-whitespace-only comparison reports 396 differences beginning at logical line 7; every difference is an export-added leading space and none remains after boundary-whitespace trimming.
- Instruction Preservation Matrix: `VERIFIED`; 106 Author rows and 44 affected Validator rows passed independent coverage and ownership review after all reported findings were corrected by the root agent on 2026-09-03.
- High-risk validation protocol: `VERIFIED` by an independent read-only subagent `PASS` and root-agent reconciliation on 2026-09-02.
- `Main_Agent.txt` scope correction: `VERIFIED` by independent read-only follow-up; canonical Main prompt integrity and Validator prompt/export parity are now also `VERIFIED`, leaving independent verification of the S1 entry-contract audit and the final S0 closure decision.
- S1 entry-contract sufficiency: `VERIFIED`; the final independent audit confirmed DEC-018 and the audit table, and the focused follow-up found no remaining contradiction.

### Relevant Files

- Continuity: `AGENTS.md`, this file, [ROADMAP.md](ROADMAP.md), the active ExecPlan, and [DECISIONS.md](../decisions/DECISIONS.md).
- Current Author authority: `Main_Agent_Prompt.txt`. `Main_Agent.txt` is a read-only legacy Pega rule export and is not a refactor deliverable.
- Current Validator: `Validator_Prompt.txt` and `JsonValidator_tool.txt`.
- Schema families: `rule-test-unit-case_JsonSchema.txt`, `rule-test-unit-case_JsonExample.txt`, `rule-test-unit-case_multInpComb-JsonSchema.txt`, and `rule-test-unit-case_multInpComb-JsonExample.txt`.
- Supporting evidence: `Rule_Crawler_tool.txt` and the rule-type Knowledge Area files in the repository root.

### Handoff

- **Repository state:** Unborn `main` branch with no tracked baseline; the current architecture remains the monolithic Author plus Validator and legacy response-record transport.
- **Active objective and stage:** S0 is closed. Create the authorized initial Git baseline before selecting S1 and preparing its ExecPlan; no S1 implementation has begun.
- **Verified work:** Repository/document inventory, Git-state inspection, standard-example syntax failure, and accepted architecture decisions.
- **Unverified or partial work:** The authorized initial baseline commit has not yet been created, and no S1 ExecPlan or product implementation has begun.
- **Uncommitted changes:** All 20 repository files are untracked. The root agent is authorized to create the initial baseline commit only after S0 closure; no commit has been created.
- **Blockers and unknowns:** Reproduction with a complete installed Draft 2020-12 or Pega validator remains unavailable. Missing Pega Memory, UUID-aware validation, and `UnitTestGenerator` exports are planned design and implementation work rather than unresolved external inputs.
- **Validation results:** All mandatory S0 checks are verified. The first final audit's three documentation findings were corrected, and focused independent follow-up returned `PASS`; the unavailable complete Draft 2020-12/Pega validator remains a recorded non-blocking tooling limitation.

#### Do Not Assume

- Do not assume a commit, tracked baseline, or usable `HEAD` exists.
- Do not assume the accepted target architecture has been implemented.
- Do not assume `WriteMemory`, `GetMemory`, UUID-aware `JsonValidationTool`, or the new agent export exists in this repository; they must be designed and created in their assigned stages.
- Do not create the authorized initial baseline commit before S0 satisfies its closure criteria.
- Do not treat local schema-keyword validation as validation by an installed full Draft 2020-12 implementation; record the distinction until equivalent tooling is available.
- Do not assume an in-scope prompt/export pair is semantically synchronized until decoded comparison is recorded. Do not treat `Main_Agent.txt` as an in-scope pair or edit target.

#### Exact next action

Create the user-authorized initial baseline commit for the verified closed S0 repository before selecting or implementing S1.

## Essential Workflow

### Session Start

1. Read this file, [ROADMAP.md](ROADMAP.md), the active ExecPlan, and relevant decisions.
2. Inspect Git and repository state.
3. Reconcile every discrepancy between recorded and observed state.
4. Identify the active stage and its first unmet mandatory acceptance criterion.
5. Set exactly one next action in this file and the active ExecPlan.

### Checkpoint

After every material project-state change:

1. Inspect Git status and the relevant diff or, while no tracked baseline exists, inspect the named files directly.
2. Record actual changes and validation results using the defined evidence classifications.
3. Update this file and affected roadmap, ExecPlan, or decision entries.
4. Keep exactly one next action.
5. Verify every recorded claim against repository evidence.

Do not update continuity files for discussion-only turns with no project-state change.

### High-Risk Change Gate

A change is high-risk when it does any of the following:

- moves, splits, replaces, or removes an existing agent instruction;
- changes a prompt, embedded `<pySystemPrompt>`, schema contract, Knowledge Area contract, Pega tool configuration, agent interface, Memory addressing, Validator route, grouping/cardinality rule, assertion rule, simulation rule, or repair policy;
- performs a broad mechanical rewrite or removes legacy behavior across multiple artifacts.

After each high-risk change or indivisible high-risk batch:

1. Stop work that depends on the change and classify it as `IMPLEMENTED_NOT_VERIFIED`.
2. Launch an independent read-only subagent with the changed files, source baseline, relevant Instruction Preservation Matrix rows, acceptance criteria, and required validation commands.
3. Require a report containing scope, evidence inspected, findings with severity and file/line references, missing or unverified checks, required corrections, and verdict `PASS`, `FAIL`, or `BLOCKED`.
4. Keep the subagent read-only. It reports to the root agent and does not modify product or global continuity artifacts.
5. The root agent verifies the report, applies corrections, reruns affected checks, and launches follow-up independent review when a blocking finding changed the high-risk behavior.
6. Promote the change to `VERIFIED` only after a `PASS` report and root-agent reconciliation. `FAIL` or `BLOCKED` prevents dependent work and stage closure.

### Stage Closure

1. Check every mandatory acceptance criterion for the active stage.
2. Run all available required validation.
3. Record commands, outputs, files, and other evidence.
4. Keep the stage open when mandatory validation is unresolved.
5. Create the next ExecPlan only after the next stage is selected.

### Project Artifact Maintenance

- Treat readable `*_Prompt.txt` files as canonical prompt sources. Synchronize a complete prompt into a paired Pega export only when that export is explicitly in the active stage's scope.
- Before splitting prompts, account for every normative source section and cross-cutting invariant in the active stage's Instruction Preservation Matrix. Every stable instruction must have a destination owner and regression check; removal requires an accepted decision and evidence that the instruction is obsolete legacy behavior.
- The current in-scope pair is `Validator_Prompt.txt` to `JsonValidator_tool.txt`. `Main_Agent.txt` is reference-only; `Main_Agent_Prompt.txt` alone is the current monolith instruction authority. Record future pairs only when their exports are selected as deliverables.
- Compare prompt/export content after HTML/XML entity decoding, including `&quot;`, `&#10;`, and `&#124;`; byte equality is not required, semantic equality is.
- Limit Pega export edits to the intended prompt or explicitly authorized tool/agent configuration. Preserve unrelated system fields and metadata and avoid whole-file reformatting.
- Preserve Knowledge Area marker IDs and cross-references. Add identifiers using the established format for that file.
- Keep schema changes valid under JSON Schema Draft 2020-12, update the matching example when affected, and validate the example against the schema.
- Preserve schema-family filenames and casing because prompts and KnowledgeTool composite keys depend on them.
- After prompt changes, verify every in-scope prompt/export pair, `<pySystemPrompt>` boundaries, and the absence of unintended export changes. For an unpaired canonical prompt, verify content integrity and instruction-matrix traceability instead.

## Minimal ExecPlan Standard

Every ExecPlan must be self-contained, implementation-oriented, evidence-based, continuously maintained, and linked to one stable Roadmap stage ID. It must contain:

- Purpose
- Scope
- Excluded Scope
- Assumptions and Unknowns
- Dependencies
- Milestones
- Progress
- Acceptance Criteria
- Validation
- Evidence
- Risks
- One concrete next-action section as the final section

The Risks section must identify each high-risk milestone and its independent subagent validation gate.

## Evidence Classifications

- `VERIFIED` — implemented or observed and confirmed by recorded evidence.
- `IMPLEMENTED_NOT_VERIFIED` — present in the repository but mandatory validation is incomplete.
- `PARTIAL` — some required work is complete, but the declared result is incomplete.
- `FAILED` — attempted validation or implementation did not satisfy its criterion.
- `BLOCKED` — progress cannot continue without an external decision, artifact, permission, or state change.
- `UNKNOWN` — current evidence is insufficient to classify the claim.
- `NOT_STARTED` — no implementation work has begun.

Never silently promote a weaker classification to a stronger one.

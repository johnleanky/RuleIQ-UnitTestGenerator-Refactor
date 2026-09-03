# Project Continuity

This file is the single authoritative operational state for resuming repository work. Keep it concise and reconcile it with repository evidence at every checkpoint.

## Current State

- **Project objective:** Refactor the current monolithic Pega unit-test Author into a Scenario Author and a Unit Test Generator, with caller-side contracts for user-implemented UUID-addressed Pega GenAI Memory and Validator tools, while preserving every stable instruction through explicit source-to-destination traceability and preserving schema-governed `UnitTestRules` output.
- **Repository root:** `C:/Dev/RuleIQ-UnitTestGenerator-Refactor/RuleIQ-UnitTestGenerator-Refactor`
- **Current branch:** `main`
- **Recorded HEAD:** `SELF` — the S1 closure commit containing this checkpoint, titled `docs: define verified Pega tool call contracts`; resolve its immutable hash with `git rev-parse HEAD`. Its parent is verified S0 baseline `99e038330076288bcc86bcc556681dc3efc82c74`.
- **Remote tracking state:** `origin/main` is reported as gone.
- **Working-tree state:** `VERIFIED` — clean immediately after the user-authorized S1 closure commit; it captures six documentation, planning, contract, and decision paths, with no product artifact modified.
- **Active stage:** None during the post-S1 closure checkpoint; `S1 — Pega GenAI Tool Invocation Contracts` is closed and S2 has not yet been selected as active.
- **Active ExecPlan:** [S1-pega-memory-transport.md](plans/S1-pega-memory-transport.md), closed and retained as the transition authority until S2 is selected and its ExecPlan is created.
- **Stage status:** `CLOSED` for S1; `NOT_STARTED` for S2.
- **Current project status:** `PARTIAL` — repository-only Pega GenAI tool-call contracts are verified, external Pega implementation remains user-owned, and product prompt refactoring has not started.

### Verified Completed Work

- `VERIFIED` — repository root, branch, unborn HEAD, remote tracking state, and initial untracked working tree were inspected on 2026-09-02.
- `VERIFIED` — no `AGENTS.override.md`, README, architecture, requirements, roadmap, ADR, plan, or task documents existed before continuity initialization.
- `VERIFIED` — the initial standard JSON example had an illegal trailing comma at line 269; this is retained as pre-fix evidence.
- `VERIFIED` — the accepted target architecture and continuity decisions are recorded in [DECISIONS.md](../decisions/DECISIONS.md).
- `VERIFIED` — the five continuity artifacts passed post-write path, link, language, stage, dependency, decision-field, next-action, and product-file-scope checks.
- `VERIFIED` — instruction-preservation and high-risk independent-validation requirements are accepted and recorded as durable decisions.
- `VERIFIED` — an independent read-only subagent reviewed the preservation and high-risk-gate additions on 2026-09-02 and returned `PASS` with no findings; the root agent reconciled the report against repository evidence.
- `VERIFIED` — the user authorized the root agent to create the initial baseline commit after S0 closure, confirmed that the new Pega exports do not exist, selected `UnitTestGenerator` as the new agent rule name, and authorized the standard-example syntax repair and schema validation. DEC-019 later assigns the three tool implementations to the user while retaining repository-owned agent-call design.
- `VERIFIED` — the 150-row Instruction Preservation Matrix passed independent review after all findings were corrected by the root agent on 2026-09-03.
- `VERIFIED` — the standard example comma defect is corrected; all four files parse, and both examples pass independently reviewed validation of every schema assertion keyword they use.
- `VERIFIED` — the 2026-09-03 restart checkpoint confirms unborn `main`, absent `HEAD`, gone `origin/main`, 20 untracked files, one active S0 stage, and one synchronized next action.
- `VERIFIED` — DEC-017 and affected stage language exclude `Main_Agent.txt` from parity, edits, and deliverables; after root correction of residual generic wording, independent follow-up review returned `PASS` on 2026-09-03.
- `VERIFIED` — the canonical `Main_Agent_Prompt.txt` baseline and decoded Validator prompt/export parity were recorded on 2026-09-03 without changing any product artifact.
- `VERIFIED` — the S1 entry-contract audit maps accepted interfaces and boundaries to evidence and records the user-confirmed opaque Payload/UUID contract as DEC-018; independent review confirmed it is sufficient to begin S1.
- `VERIFIED` — the first final S0 audit found three planning-document inconsistencies; the root corrected them, and focused independent follow-up returned `PASS` with no findings.
- `VERIFIED` — all mandatory S0 acceptance criteria are satisfied and S0 is closed as of 2026-09-03.
- `VERIFIED` — initial baseline commit `99e038330076288bcc86bcc556681dc3efc82c74` was created after S0 closure and before S1 activation; its tree contains all 20 baseline files.
- `NOT_STARTED` — product prompt, schema, and Pega agent-export changes; implementation of the three external tools is no longer a repository deliverable.
- `PARTIAL` — S1 discovery identified the local export boundary and authoritative Rule-AI-Tool schema, but live application and rule listings timed out.
- `VERIFIED` — the user assigned Pega tool implementation and backing configuration to themselves, selected repository-only work, and limited this project to designing agent calls to those external GenAI tools; DEC-019 records the boundary.
- `VERIFIED` — an independent read-only review of the DEC-019 scope revision returned `PASS` after the root corrected one residual S0 creation statement and one S1/S5 runtime-boundary statement; no product file changed.
- `VERIFIED` — the repository caller contract and F01–F13 static fixtures at [PEGA_GENAI_TOOL_CALL_CONTRACTS.md](../contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md) passed focused independent follow-up after all first-review defects were corrected and root static checks passed.
- `VERIFIED` — every mandatory S1 acceptance criterion is satisfied and S1 is closed as of 2026-09-03.
- `VERIFIED` — the user-authorized commit `docs: define verified Pega tool call contracts` captures the complete S1 checkpoint in six documentation paths; its self-referential hash is resolved from Git rather than embedded in its own contents.

### Blockers and Unknowns

- `UNKNOWN` — whether an installed full Draft 2020-12 validator or runnable Pega JsonValidationTool can reproduce the local schema-keyword validation; none is currently available without installing dependencies.
- `VERIFIED` — the detailed caller-side specification and static fixtures for `WriteMemory`, `GetMemory`, and UUID-aware `JsonValidationTool` passed root validation and focused independent review.
- `VERIFIED` — the independently reviewed S1 entry-contract audit found no decision gap in immutable exact addressing or opaque round trips; DEC-019 now excludes backing categories, rules, storage, exports, ChangeRequests, and runtime proof from repository scope.
- `UNKNOWN` — exact Pega backing implementation and runtime behavior remain user-owned and external; they cannot be claimed as repository-verified and do not block S1 caller-contract design or closure.

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
- `Main_Agent.txt` scope correction: `VERIFIED` by independent read-only follow-up; canonical Main prompt integrity, Validator prompt/export parity, S1 entry-contract sufficiency, and final S0 closure are also `VERIFIED`.
- S1 entry-contract sufficiency: `VERIFIED`; the final independent audit confirmed DEC-018 and the audit table, and the focused follow-up found no remaining contradiction.
- S1 activation-plan review: `FAILED`; the first independent review found one missing post-design gate and two stale continuity classifications, requiring root corrections and focused follow-up.
- S1 activation-plan follow-up: `VERIFIED`; focused independent review returned `PASS` with no findings, confirmed the pre-implementation design gate, and reproduced unchanged product hashes.
- S1 export/runtime discovery: `PARTIAL`; local exports and Pega Rule-AI-Tool schema were inspected, but application and rule-list calls timed out after 120 seconds and no backing rule could be validated.
- S1 scope decision: `VERIFIED`; explicit user direction selects repository-only caller-contract work and external user-owned Pega implementation, recorded in DEC-019; independent read-only review returned `PASS` with no remaining findings.
- S1 caller-contract design: `VERIFIED`; the specification and F01–F13 fixtures passed root static validation and focused independent follow-up.
- S1 caller-contract first review: `FAILED`; it found overlapping validation error semantics, an incomplete candidate-read ValidatorReport mapping, lost mass-error compaction, missing partial-result mapping, and one stale continuity classification.
- S1 caller-contract follow-up: `VERIFIED`; all prior findings were corrected, 13 JSON examples parse, F01–F13 and every IPM reference resolve, product hashes match HEAD, links and exact-next-action checks pass, and the independent reviewer returned `PASS`.

### Relevant Files

- Continuity: `AGENTS.md`, this file, [ROADMAP.md](ROADMAP.md), the active ExecPlan, and [DECISIONS.md](../decisions/DECISIONS.md).
- S1 caller contract: [PEGA_GENAI_TOOL_CALL_CONTRACTS.md](../contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md).
- Current Author authority: `Main_Agent_Prompt.txt`. `Main_Agent.txt` is a read-only legacy Pega rule export and is not a refactor deliverable.
- Current Validator: `Validator_Prompt.txt` and `JsonValidator_tool.txt`.
- Schema families: `rule-test-unit-case_JsonSchema.txt`, `rule-test-unit-case_JsonExample.txt`, `rule-test-unit-case_multInpComb-JsonSchema.txt`, and `rule-test-unit-case_multInpComb-JsonExample.txt`.
- Supporting evidence: `Rule_Crawler_tool.txt` and the rule-type Knowledge Area files in the repository root.

### Handoff

- **Repository state:** `main` is at the clean S1 closure commit `docs: define verified Pega tool call contracts`, whose parent is baseline `99e038330076288bcc86bcc556681dc3efc82c74`; the current product architecture remains the monolithic Author plus Validator and legacy response-record transport.
- **Active objective and stage:** S1 is closed. Select S2 and create its ExecPlan before changing Scenario Author prompts; Pega backing implementation remains user-owned and out of scope.
- **Verified work:** Repository/document inventory, Git-state inspection, standard-example syntax failure, and accepted architecture decisions.
- **Unverified or partial work:** S2–S5 product prompt, agent-export, Validator, and integration changes have not started; Pega runtime behavior is external and will not be claimed as repository-verified.
- **Uncommitted changes:** None immediately after the S1 closure commit; product files remain unchanged.
- **Blockers and unknowns:** No blocker prevents selection and planning of S2. Exact Pega implementation metadata and runtime behavior remain external dependencies for later integration.
- **Validation results:** All mandatory S0 and S1 checks are verified. The S1 caller contract passed root static checks and focused independent follow-up after the first review's findings were corrected.

#### Do Not Assume

- Do not assume the repository is still unborn: verify and use baseline HEAD `99e038330076288bcc86bcc556681dc3efc82c74` unless Git evidence shows a later authorized commit.
- Do not assume the accepted target architecture has been implemented.
- Do not assume `WriteMemory`, `GetMemory`, or UUID-aware `JsonValidationTool` exists in this repository or create their Pega implementation here; the user owns them externally under DEC-019. The new agent export remains assigned to its later stage.
- Do not create the authorized initial baseline commit before S0 satisfies its closure criteria.
- Do not treat local schema-keyword validation as validation by an installed full Draft 2020-12 implementation; record the distinction until equivalent tooling is available.
- Do not assume an in-scope prompt/export pair is semantically synchronized until decoded comparison is recorded. Do not treat `Main_Agent.txt` as an in-scope pair or edit target.

#### Exact next action

Select S2 as the next active Roadmap stage and create its ExecPlan before changing Scenario Author product artifacts.

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

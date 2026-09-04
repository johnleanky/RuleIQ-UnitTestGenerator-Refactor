# Project Continuity

This file is the single authoritative operational state for resuming repository work. Keep it concise and reconcile it with repository evidence at every checkpoint.

## Current State

- **Project objective:** Refactor the current monolithic Pega unit-test Author into a Scenario Author and a Unit Test Generator, with caller-side contracts for user-implemented UUID-addressed Pega GenAI Memory and Validator tools, while preserving every stable instruction through explicit source-to-destination traceability and preserving schema-governed `UnitTestRules` output.
- **Repository root:** `C:/Dev/RuleIQ-UnitTestGenerator-Refactor/RuleIQ-UnitTestGenerator-Refactor`
- **Current branch:** `main`
- **Recorded HEAD:** the reviewer-model governance checkpoint commit containing this file; resolve the exact hash with `git rev-parse HEAD` because a commit cannot embed its own hash. Its verified parent is `36f097a842296b0e9b4de30cbb1ce27046c5ff0c`.
- **Remote tracking state:** `main` tracks `origin/main`, and the reviewer-model governance checkpoint is pushed.
- **Working-tree state:** `VERIFIED` — clean immediately after the reviewer-model governance checkpoint commit and push; no product file changed in that checkpoint.
- **Active stage:** none at the verified S2/S3 planning boundary.
- **Active ExecPlan:** none; the closed S2 plan is [S2-scenario-author-extraction.md](plans/S2-scenario-author-extraction.md).
- **Stage status:** `S2` is `CLOSED`; `S3` is `NOT_STARTED`.
- **Current project status:** `VERIFIED` — Scenario Author extraction remains verified and pushed, and the reviewer-model policy passed focused independent follow-up after correction of one Roadmap/continuity conflict. UnitTestGenerator implementation has not begun.

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
- `PARTIAL` — the first bounded `Main_Agent_Prompt.txt` refactor batch is implemented; schema and Pega agent-export changes remain not started, and implementation of the three external tools is not a repository deliverable.
- `PARTIAL` — S1 discovery identified the local export boundary and authoritative Rule-AI-Tool schema, but live application and rule listings timed out.
- `VERIFIED` — the user assigned Pega tool implementation and backing configuration to themselves, selected repository-only work, and limited this project to designing agent calls to those external GenAI tools; DEC-019 records the boundary.
- `VERIFIED` — an independent read-only review of the DEC-019 scope revision returned `PASS` after the root corrected one residual S0 creation statement and one S1/S5 runtime-boundary statement; no product file changed.
- `VERIFIED` — the repository caller contract and F01–F13 static fixtures at [PEGA_GENAI_TOOL_CALL_CONTRACTS.md](../contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md) passed focused independent follow-up after all first-review defects were corrected and root static checks passed.
- `VERIFIED` — every mandatory S1 acceptance criterion is satisfied and S1 is closed as of 2026-09-03.
- `VERIFIED` — the user-authorized commit `docs: define verified Pega tool call contracts` captures the complete S1 checkpoint in six documentation paths; its self-referential hash is resolved from Git rather than embedded in its own contents.
- `VERIFIED` — S2 activation revalidated the clean HEAD `b9dd5653f4c449653ac14e06c595e5e2108f516a`, unchanged canonical Main prompt hash/size/line count, and the 106-row Author partition of 48 Scenario Author, 39 shared, 18 Generator, and one Validator owner.
- `VERIFIED` — the corrected S2 activation plan passed focused independent follow-up with no remaining findings; the reviewer confirmed exact DEC-016 requirements, DEC-017-compliant S5 scope, the closed Scenario Author tool allowlist, synchronized next action, matrix counts, and unchanged product artifacts.
- `VERIFIED` — all 106 Scenario Author matrix rows, the ScenarioGroup v1 contract, final storage/handoff boundary, fixtures, and deterministic checker passed independent final follow-up and root reconciliation on 2026-09-04; S2 is closed.
- `VERIFIED` — the authorized S2 closure checkpoint is committed on `main` and pushed to `origin`; obtain its exact self-referential commit hash from Git.
- `VERIFIED` — the user selected explicit model profiles for future independent repository reviewers on 2026-09-04; DEC-022 records the accepted policy.
- `VERIFIED` — the reviewer-model policy and its Roadmap synchronization correction passed read-only `gpt-5.6-sol`/`xhigh` focused follow-up with no remaining findings.
- `VERIFIED` — the independently verified reviewer-model governance update is committed on `main` and pushed to `origin`; obtain its exact self-referential commit hash from Git.

### Blockers and Unknowns

- `UNKNOWN` — whether an installed full Draft 2020-12 validator or runnable Pega JsonValidationTool can reproduce the local schema-keyword validation; none is currently available without installing dependencies.
- `VERIFIED` — the detailed caller-side specification and static fixtures for `WriteMemory`, `GetMemory`, and UUID-aware `JsonValidationTool` passed root validation and focused independent review.
- `VERIFIED` — the independently reviewed S1 entry-contract audit found no decision gap in immutable exact addressing or opaque round trips; DEC-019 now excludes backing categories, rules, storage, exports, ChangeRequests, and runtime proof from repository scope.
- `UNKNOWN` — exact Pega backing implementation and runtime behavior remain user-owned and external; they cannot be claimed as repository-verified and do not block S1 caller-contract design or closure.
- `VERIFIED` — the complete corrected S2 design-freeze package received focused independent `PASS`; the reviewer mutation-tested the DEC-020/IPM-AUTH-041/S2-R041 link, reproduced 106 executable row checks and all static fixtures, and confirmed unchanged product files and repository-only scope.
- `VERIFIED` — the first bounded prompt batch replaces monolithic role, candidate/Validator loop, interfaces, source order, and execution outline with Scenario Author ownership, exact ScenarioGroup writes, one UnitTestGenerator handoff, a five-interface closed allowlist, downstream-only legacy locks, and bounded result mapping. Its 26 IPM rows passed independent review and are verified.
- `VERIFIED` — prompt batch 2 refactors semantic Knowledge acquisition, evidence/dependency/runtime records, assertion/simulation/omission decisions, Scenario Compiler state, grouping semantics, summary facts, and confidence/testability. All 66 rows passed focused independent follow-up; materialization/handoff is implemented separately in the final batch.
- `VERIFIED` — no external blocker prevents S2 repository planning or design; Pega runtime remains external under DEC-019.

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
- S2 activation plan: `VERIFIED`; after the first review found missing test locks for DEC-016, conflicting S5 legacy-search scope, and an open Scenario Author allowlist, the root corrected all three and focused independent follow-up returned `PASS` with no findings.
- S2 design-freeze package: `IMPLEMENTED_NOT_VERIFIED`; the first independent review returned `FAIL` despite the initial root-check `PASS`. Blocking gaps cover exact S1 WriteMemory envelopes, runtime-complete/no-simulation When grouping keys, When cell/trace bijection, atomic Decision Table consumer/action/setup reconciliation, and structured parameter/root/complexity/EvidenceSummary facts. Medium findings cover non-null enforcement, deterministic ID freeze rules, and row-specific regression/destination proof.
- S2 design-freeze first corrections: `FAILED`; the second focused review confirmed the first review's envelope, grouping-key, cell/trace, Decision Table, structured-fact, and non-null corrections, but found four high and two medium residual defects: the 106 check labels are not executable definitions and the slice contains `NaN`; the checker wrongly requires equal signatures across unequal simulation groups; SIM trace projection is not an exact whitelist; COMPLEXITY derivation is incomplete; the contract omits the `C` ID prefix; and `dtCount` prose omits DTC.
- S2 design-freeze second corrections: `IMPLEMENTED_NOT_VERIFIED`; the slice now contains 106 exact executable check definitions and no placeholder; cross-group signature equality is removed while within-group checks remain; AssertionDecisionTrace uses exact tag-specific whitelists with positive and contaminated SIM cases; DEC-020 closes loop/invocation and cap derivation with six boundary cases; and contract prose now includes `C` COLUMN and DTC. The expanded checker, JSON parsing, exact-next synchronization, product hash/scope, whitespace, and link checks pass locally; focused independent follow-up is pending.
- S2 design-freeze third review: `FAILED`; it passed every prior functional correction, product integrity, scope, exact-next, and local checker result, but found that the new DEC-020 behavior lacks reverse traceability from IPM-AUTH-041 and S2-R041. No product file changed.
- S2 design-freeze third correction: `IMPLEMENTED_NOT_VERIFIED`; IPM-AUTH-041 and S2-R041 now cite DEC-020, all 106 executable audits include and validate their exact decision sets, and a specific checker assertion prevents removal of the DEC-020 linkage. Expanded checker, diff check, exact-next synchronization, and product-scope checks pass locally.
- S2 design-freeze final follow-up: `VERIFIED`; independent review returned `PASS` with no remaining findings, reproduced the checker, and confirmed both temporary DEC-020-removal mutations fail as required. External Pega runtime and post-prompt row execution remain intentionally unverified.
- S2 prompt batch 1 local validation: `IMPLEMENTED_NOT_VERIFIED`; expanded checker passes role, authority, exact WriteMemory envelope/call order, Generator mapping, closed allowlist, 20-step execution order, 26 prompt trace markers, and the Sections 5–14 semantic-scope lock. `Main_Agent_Prompt.txt` is SHA-256 `51126AB5836E4D7DB9D0C54E5C729E9F59D25AC25B871E5982022F692868B133`, 166,207 bytes, and 2,068 logical lines with CRLF and no BOM; no other `.txt` differs from HEAD.
- S2 prompt batch 1 first review: `FAILED`; behavioral checks passed, but two medium coherence defects remained: continuity/plan still contained four stale `NOT_STARTED` or unchanged-product statements, and the prompt falsely claimed the full ScenarioGroup grammar was embedded even though insertion belongs to the later materialization batch.
- S2 prompt batch 1 corrections: `IMPLEMENTED_NOT_VERIFIED`; stale classifications are reconciled, and the prompt now truthfully states that the full repository-defined grammar will be inserted in the later materialization batch, marks the intermediate prompt non-release-ready, and blocks WriteMemory/Generator execution until insertion. The checker enforces these statements. Root checks pass at SHA-256 `4A052FD0F5159728F37A9D18BE610776237E9E7D2792222213FE202C60554326`, 166,730 bytes, and 2,068 CRLF lines.
- S2 prompt batch 1 follow-up: `VERIFIED`; independent review returned `PASS` with no remaining findings, confirmed all state corrections and truthful deferred-grammar gates, reproduced the checker and product scope, and verified the prompt hash/encoding. IPM-AUTH-001–020 and 027–032 are now verified.
- S2 prompt batch 2 local validation: `IMPLEMENTED_NOT_VERIFIED`; expanded checker passes semantic-only KnowledgeTool keys/checkpoints, evidence/dependency scope, simulation decisions, internal `SCENARIO_SNAPSHOT`, physical grouping, final SUMMARY/ASSERT/SIM/OMIT semantics, omission catalog, confidence caps, and 66 additional IPM traces. The prompt has SHA-256 `8972DF766EF2837DE7DBEBE859A172D749C5B75EE45D48F7ABCAC1756A69AF06`, 157,467 bytes, and 1,920 CRLF logical lines; it is the only changed product `.txt`.
- S2 prompt batch 2 first review: `FAILED`; two high defects make semantic AUDITED unreachable without forbidden candidate work and leave DEC-020 under-specified in the runtime prompt. Two medium defects leave ROOT circular through RuleCode and checker coverage too shallow. The other 66-row semantic behaviors, scope, product integrity, and repository boundary passed.
- S2 prompt batch 2 corrections: `IMPLEMENTED_NOT_VERIFIED`; execution now runs I/W/F before final decisions and B/A after complete semantic materialization but before WriteMemory; B/A audit ScenarioGroup records with no RuleCode/candidate/tool carrier; exact DEC-020 triggers, tiers, caps, and limits are embedded; ROOT derives directly from evidenced primary-page semantics; and 14 critical prompt mutations prove checker coverage. Root checks pass at SHA-256 `D3356E2D8A26E1AF7FB98AAA4641255263FC7D867E6B6AA8C7581ED1217F1BD3`, 159,680 bytes, and 1,929 CRLF lines.
- S2 prompt batch 2 second review: `FAILED`; all three product-prompt corrections passed, but one medium checker defect remains because mutations do not cover the full hard-trigger thresholds, exact tier derivation, complete ROOT freeze/named-page rule, weighted formula, or the full RuleCode-independence prohibition.
- S2 prompt batch 2 checker correction: `IMPLEMENTED_NOT_VERIFIED`; the checker now requires and mutation-tests 16 complete atomic clauses, including all six DEC-020 derivation clauses and all seven ROOT-lock clauses in their required sections. The repository-static checker and `git diff --check` pass locally; focused independent review is pending.
- S2 prompt batch 2 checker first focused audit: `FAILED`; the reviewer reproduced two medium defects: two workflow clauses were not section-bound, and the ELEVATED wording `25–49` did not close the fractional-score interval permitted by the weighted formula.
- S2 prompt batch 2 checker follow-up correction: `IMPLEMENTED_NOT_VERIFIED`; all three workflow clauses are now bound to their required execution/compiler sections, all 16 critical clauses have relocation mutations, ELEVATED is exact at `25 <= score < 50`, and explicit 49.75/50 fixtures close the score boundary. Root checks pass with `Main_Agent_Prompt.txt` SHA-256 `B88678FE2776D494288CB06BD86D2840107313DCBAB9A1825998E6EA79F62E75`, 159,680 bytes, and 1,929 CRLF logical lines; focused independent follow-up is pending.
- S2 prompt batch 2 checker follow-up: `VERIFIED`; independent review returned `PASS` with no findings and rejected 96 adversarial removals, relocations, duplicates, and DEC-020/ROOT fragment mutations. All 66 batch-2 IPM rows are verified; validation remains repository-static.
- S2 completion strategy: `VERIFIED`; the user accepted one consolidated final high-risk batch with integrity-only rechecks of untouched verified sections, one full independent audit, and a mandatory authorized commit/push after S2 closure. DEC-021 records the durable rule.
- S2 final prompt batch initial snapshot: `IMPLEMENTED_NOT_VERIFIED`; it removed the legacy candidate/Validator tail and added final semantic gates, the executable ScenarioGroup v1 contract, ordered storage/handoff, a closed Author prohibition, and downstream ownership. The later full audit failed and superseded this intermediate hash and classification.
- S2 full final audit: `FAILED`; three high findings identified a non-executable 106-row regression claim, an unmaterializable NotTestable state, and unchecked dangling RX/PROPERTY references. Two medium findings identified zero-PARAM, RequiredButLimited/NotApplicable, DTA-OMIT checker gaps and stale operational classifications.
- S2 final-audit correction follow-up: `VERIFIED`; the checker freezes the independently reviewed 106-row prompt by full SHA-256/CRLF regression, resolves RX/BRANCH/PRODUCER/PROPERTY references, allows zero PARAM rows, models NotTestable and schema-aligned SupportLevel values, constrains all four simulation states, and exercises DTA-to-OMIT. Focused independent follow-up returned `PASS` with no high- or medium-severity findings. The final prompt is 174,283 bytes and 1,973 CRLF logical lines with no BOM and SHA-256 `BACADFB07E90D68B9751B9D573437A21B204E0BCCE87BE6ACE8BD5DDF3CEEC95`. Pega runtime remains external and unverified.
- S2 final root reconciliation and closure: `VERIFIED`; the S2 checker, all five JSON files, prompt hash/encoding, 106-row census, product scope, unchanged `Main_Agent.txt`, cache hygiene, and `git diff --check` passed on 2026-09-04 before the authorized checkpoint commit and push.

### Relevant Files

- Continuity: `AGENTS.md`, this file, [ROADMAP.md](ROADMAP.md), the active ExecPlan, and [DECISIONS.md](../decisions/DECISIONS.md).
- S1 caller contract: [PEGA_GENAI_TOOL_CALL_CONTRACTS.md](../contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md).
- S2 closed plan: [S2-scenario-author-extraction.md](plans/S2-scenario-author-extraction.md).
- S2 implementation slice: [S2-instruction-implementation-slice.md](design/S2-instruction-implementation-slice.md).
- ScenarioGroup v1 contract: [SCENARIO_GROUP_V1.md](../contracts/SCENARIO_GROUP_V1.md).
- Current Author authority: `Main_Agent_Prompt.txt`. `Main_Agent.txt` is a read-only legacy Pega rule export and is not a refactor deliverable.
- Current Validator: `Validator_Prompt.txt` and `JsonValidator_tool.txt`.
- Schema families: `rule-test-unit-case_JsonSchema.txt`, `rule-test-unit-case_JsonExample.txt`, `rule-test-unit-case_multInpComb-JsonSchema.txt`, and `rule-test-unit-case_multInpComb-JsonExample.txt`.
- Supporting evidence: `Rule_Crawler_tool.txt` and the rule-type Knowledge Area files in the repository root.

### Handoff

- **Repository state:** `main` contains the pushed reviewer-model governance checkpoint, and the working tree is clean immediately after that checkpoint; no product file changed.
- **Active objective and stage:** No Roadmap stage is active at the S2/S3 boundary. The next objective is to create and independently validate the S3 ExecPlan before Generator implementation.
- **Verified work:** S0 and S1 are closed. S2 Scenario Author extraction, ScenarioGroup materialization, ordered Memory handoff, instruction preservation, independent validation, root reconciliation, commit, and push are complete.
- **Unverified or partial work:** S3 UnitTestGenerator, S4 Validator refactor, S5 integration/cleanup, and external Pega runtime behavior remain not started or external.
- **Uncommitted changes:** None immediately after the reviewer-model governance checkpoint.
- **Blockers and unknowns:** No repository blocker. Pega runtime remains external and unverified under DEC-019.
- **Validation results:** All S2 static checks and independent review gates pass. The first reviewer-model policy audit returned `FAIL` on one medium Roadmap/continuity synchronization defect; focused `gpt-5.6-sol`/`xhigh` follow-up returned `PASS` with no findings after correction.

#### Do Not Assume

- Do not assume the repository is still at the S2 closure commit: resolve the current reviewer-model governance checkpoint hash and remote state from Git.
- Do not assume the full target architecture is implemented: Scenario Author is complete, while UnitTestGenerator and Validator refactors remain future stages.
- Do not assume `WriteMemory`, `GetMemory`, or UUID-aware `JsonValidationTool` exists in this repository or create their Pega implementation here; the user owns them externally under DEC-019. The new agent export remains assigned to its later stage.
- Do not create another commit unless the user explicitly authorizes it.
- Do not treat local schema-keyword validation as validation by an installed full Draft 2020-12 implementation; record the distinction until equivalent tooling is available.
- Do not assume an in-scope prompt/export pair is semantically synchronized until decoded comparison is recorded. Do not treat `Main_Agent.txt` as an in-scope pair or edit target.

#### Exact next action

Create and independently validate the S3 ExecPlan before activating S3 or changing `UnitTestGenerator` product artifacts.

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

#### Independent Reviewer Model Profiles

Pass both the model and reasoning effort explicitly when spawning an independent repository reviewer:

- routine documentation-only review: `gpt-5.6-terra` with `high` reasoning;
- high-risk change or indivisible high-risk batch: `gpt-5.6-sol` with `xhigh` reasoning;
- final whole-stage closure audit: `gpt-5.6-sol` with `max` reasoning.

These profiles apply to repository validation subagents, not the Pega Validator agent. Do not silently substitute a model or reasoning effort. If the required profile is unavailable, record the gate as `BLOCKED` and request user direction.

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

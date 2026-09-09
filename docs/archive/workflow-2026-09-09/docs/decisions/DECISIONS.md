# Decision Log

This is an append-oriented log. Add accepted durable decisions; do not record unresolved ideas as decisions. Supersede prior entries explicitly instead of rewriting their historical meaning.

## DEC-033 — Resolve Data Page Inputs at Each Access

- **Status:** ACCEPTED by the user's implementation request; S6 design/activation IMPLEMENTED_NOT_VERIFIED pending independent review.
- **Context:** The simulation exposed a bare Data Page reference incorrectly treated as parameterless and a source checker requiring dummy parameter references for empty maps. The user confirms implicit current-Param binding for declared inputs in the target RuleIQ environment.
- **Decision:** Implement [revision 1.4](../contracts/SCENARIO_GROUP_V1_4.md): explicit expression, present current Param, then evidenced runtime default; unresolved expressions do not fall through. Preserve timing and producer provenance, typed values, optional omissions backed by metadata, and unknown versus empty declarations. Add default PARAM mode and evidence-backed nullable SIM.parameterResolutions. Author owns acquisition/execution; Generator audits immutable facts; Validator retains candidate-only evidence limits.
- **Consequences:** Supersede only affected revision-1.3 binding/nullable/revision requirements in current products; preserve historical contracts/fixtures and gates at fixed baseline. No Memory/candidate API changes or metadata-field invention. Do not seed RUT-produced values or change scenario scope during parameter refinement. Other simulation and Validator fixes remain separate.
- **Evidence:** User-approved implementation plan and confirmed RuleIQ convention; baseline 13b44c7; [S6 ExecPlan](../execution/plans/S6-data-page-parameters.md). Static consistency and Pega runtime evidence remain distinct.

## DEC-001 — Split Semantic Authoring from Unit Test Serialization

- **Status:** `ACCEPTED`
- **Context:** The current Author combines RUT analysis, scenario design, RuleCode serialization, persistence, validation, and repair.
- **Decision:** Split it into Scenario Author and Unit Test Generator. Scenario Author owns semantic analysis and final scenarios; Generator owns schema-compatible UnitTestRules projection.
- **Reasoning:** The boundary prevents duplicated semantic reasoning and supports independent generation from materialized scenario records.
- **Consequences:** Existing Author instructions must be partitioned by ownership, and a new Generator agent must be introduced.
- **Affected stages or files:** `S2`, `S3`, `S5`; current Author prompt/export and future Generator prompt/export.
- **Evidence or references:** Approved Plan Mode architecture discussion recorded on 2026-09-02; `docs/execution/ROADMAP.md`.

## DEC-002 — Use Immutable UUID-Addressed Memory Tools

- **Status:** `ACCEPTED`
- **Context:** Legacy candidate transport is keyed only by CaseID and cannot safely identify multiple groups or candidate versions.
- **Decision:** Use `WriteMemory(CaseID, Type, Payload)` and `GetMemory(CaseID, Type, UUID)`. Writes create immutable records and return generated UUIDs; reads require an exact CaseID, Type, and UUID match.
- **Reasoning:** Explicit version identity removes latest-record ambiguity and prepares the workflow for future parallel execution.
- **Consequences:** Automatic write retries are unsafe without an idempotency key; tools must never fall back to the latest record.
- **Affected stages or files:** `S1`, `S2`, `S3`, `S4`, `S5`; Pega Memory tools and agent tool configurations.
- **Evidence or references:** Approved Plan Mode interface decisions recorded on 2026-09-02.

## DEC-003 — Use Two Memory Record Types in v1

- **Status:** `ACCEPTED`
- **Context:** Scenario handoff records and generated candidates have different owners and consumers.
- **Decision:** Use exact Memory Type values `ScenarioGroup` and `UnitTestCandidate` in the first release.
- **Reasoning:** The names preserve the physical unit-test grouping boundary and distinguish semantic source records from serialized candidates.
- **Consequences:** All writers and readers must validate Type as well as CaseID and UUID.
- **Affected stages or files:** `S1` through `S5`; Memory tool contracts and all three agent prompts.
- **Evidence or references:** Approved Plan Mode Memory-type decision recorded on 2026-09-02.

## DEC-004 — Use One ScenarioGroup per Physical Unit Test Group

- **Status:** `ACCEPTED`
- **Context:** Non-When unit tests contain one scenario, while Rule-Obj-When unit tests can contain multiple scenarios sharing one simulation configuration.
- **Decision:** Persist one ScenarioGroup per physical unit-test group. v1 uses one sequential Generator that consumes an ordered UUID array and saves one combined `{ "UnitTestRules": [...] }` candidate.
- **Reasoning:** This matches current output schemas while retaining a future fan-out boundary at ScenarioGroup granularity.
- **Consequences:** A deterministic parallel fan-out/fan-in aggregator is deferred; group order must remain stable.
- **Affected stages or files:** `S2`, `S3`, `S5`; ScenarioGroup contract and Generator interface.
- **Evidence or references:** Approved Plan Mode grouping and v1 orchestration decisions recorded on 2026-09-02.

## DEC-005 — Materialize a Versioned Final Semantic Snapshot

- **Status:** `ACCEPTED`
- **Context:** Current scenario state is split between transient ScenarioTrace memory and other internal evidence ledgers.
- **Decision:** Store ScenarioGroup Payload as a versioned line-ledger containing RUT context, grouping, final scenarios, inputs, setup, simulations, ASSERT/SIM/OMIT decisions, and sufficient final evidence. Exclude transient crawl planning and drafts.
- **Reasoning:** Generator requires a complete immutable semantic handoff without receiving a new schema-governed JSON artifact or repeating RUT analysis.
- **Consequences:** The ledger needs explicit row grammar, escaping, stable IDs, a semantic audit gate, and version validation.
- **Affected stages or files:** `S0`, `S2`, `S3`, `S4`; Scenario Author and Generator prompts.
- **Evidence or references:** Approved Plan Mode payload-depth and encoding decisions recorded on 2026-09-02.

## DEC-006 — Limit Generator Repair to Projection

- **Status:** `ACCEPTED`
- **Context:** Validator may find both mechanical serialization defects and defects requiring new semantic decisions.
- **Decision:** Generator may repair JSON shape, Pega field mapping, names, indices, and RuleCode alignment to existing ASSERT/SIM/OMIT decisions. It may not change expected values, coverage, assertions, simulations, or dependency conclusions. A non-isolatable shared When defect rejects the whole group.
- **Reasoning:** Allowing semantic repair would recreate the monolithic Author and undermine immutable handoff records.
- **Consequences:** Scenario-local defects may remove one scenario; group-shared defects remove all scenarios in that group; candidate-wide failures terminate the run.
- **Affected stages or files:** `S3`, `S4`, `S5`; Generator and Validator contracts.
- **Evidence or references:** Approved Plan Mode repair-scope and shared-group-failure decisions recorded on 2026-09-02.

## DEC-007 — Address Validator Input by Candidate UUID

- **Status:** `ACCEPTED`
- **Context:** Validator and JsonValidationTool must inspect the same candidate version across repair iterations.
- **Decision:** Validator accepts CaseID, immutable original RUTType, and candidate UUID. Routes are `OK`, `GENERATOR_REPAIR`, `SEMANTIC_REJECT`, and `HUMAN`, with precedence `HUMAN > SEMANTIC_REJECT > GENERATOR_REPAIR > OK`.
- **Reasoning:** UUID addressing eliminates races, and role-specific routes make repair ownership explicit.
- **Consequences:** Existing AUTHOR routes and CaseID-only response reads must be removed; issue indices determine scenario, group, or candidate scope.
- **Affected stages or files:** `S1`, `S3`, `S4`, `S5`; Validator prompt/export and JsonValidationTool.
- **Evidence or references:** Approved Plan Mode Validator API decision recorded on 2026-09-02.

## DEC-008 — Keep Partial-Failure Reporting Runtime-Only

- **Status:** `ACCEPTED`
- **Context:** Failed scenarios must remain in their immutable ScenarioGroup source but must not block valid scenarios from producing unit tests.
- **Decision:** Generator returns `Completed`, `PartiallyCompleted`, or `Failed` with runtime success and untestable-scenario details. It does not persist a separate result record. Scenario Author maps Generator `Completed` and `PartiallyCompleted` to the existing external `Completed` status.
- **Reasoning:** This preserves the existing external two-field status contract while allowing partial internal progress.
- **Consequences:** Partial-failure details are ephemeral after the agent call and are not exposed by the outer status object.
- **Affected stages or files:** `S3`, `S5`; Generator report and Scenario Author result handling.
- **Evidence or references:** Approved Plan Mode report-persistence and outer-status decisions recorded on 2026-09-02.

## DEC-009 — Write Repository Artifacts in English

- **Status:** `ACCEPTED`
- **Context:** Chat communication may occur in Russian, but repository artifacts require one maintenance language.
- **Decision:** Write plans, documentation, prompts, decision records, and all other repository artifacts in English.
- **Reasoning:** A single artifact language improves portability and avoids mixed-language contracts.
- **Consequences:** Russian is limited to chat communication unless this decision is explicitly superseded.
- **Affected stages or files:** All stages and repository documentation or product artifacts.
- **Evidence or references:** Explicit user requirement issued on 2026-09-02.

## DEC-010 — Use a Five-File Continuity Framework

- **Status:** `ACCEPTED`
- **Context:** Project state must survive chat restarts without duplicate state, handoff, workflow, or planning documents.
- **Decision:** Use only `AGENTS.md`, `docs/execution/CONTINUITY.md`, `docs/execution/ROADMAP.md`, one active stage ExecPlan under `docs/execution/plans/`, and this append-oriented decision log for continuity.
- **Reasoning:** One operational state file plus progressively disclosed roadmap, execution, and decision records minimizes context load and conflicting authorities.
- **Consequences:** Do not create competing `PROJECT_STATE.md`, `HANDOFF.md`, `WORKFLOW.md`, `PLANS.md`, or equivalent state files. The root agent alone edits global continuity artifacts.
- **Affected stages or files:** All stages; the five continuity artifacts.
- **Evidence or references:** Explicit continuity-framework requirements approved for implementation on 2026-09-02.

## DEC-011 — Require Complete Instruction Preservation Traceability

- **Status:** `ACCEPTED`
- **Context:** Splitting the monolithic Author by role does not by itself prove that its stable instructions and cross-cutting invariants survive the refactor.
- **Decision:** Before product prompt changes, build an Instruction Preservation Matrix covering every normative section and cross-cutting contract in the monolithic Author prompt and every affected Validator contract. Each row records classification, destination owner, migration action, target location, regression evidence, and status.
- **Reasoning:** Forward and reverse traceability makes instruction loss, accidental duplication, and ownership conflicts detectable before and after the split.
- **Consequences:** Product prompt splitting is blocked until matrix coverage is complete and independently reviewed. Removal is allowed only for accepted obsolete legacy behavior with explicit evidence.
- **Affected stages or files:** `S0`, `S2`, `S3`, `S4`, `S5`; active S0 ExecPlan, current prompts, and future split prompts.
- **Evidence or references:** User-confirmed preservation requirement recorded on 2026-09-02; `docs/execution/ROADMAP.md`; `docs/execution/plans/S0-baseline-contracts.md`.

## DEC-012 — Require Independent Validation after High-Risk Changes

- **Status:** `ACCEPTED`
- **Context:** Prompt partitioning, interface changes, schema changes, tool configuration, routing, grouping, and legacy removal can introduce defects that are difficult for the implementing agent to detect.
- **Decision:** After each high-risk change or indivisible high-risk batch, stop dependent work and launch an independent read-only subagent. The subagent reports evidence, severity-ranked findings, missing checks, required corrections, and a `PASS`, `FAIL`, or `BLOCKED` verdict to the root agent. The root agent is the sole writer and applies all corrections.
- **Reasoning:** Independent review reduces confirmation bias while preserving one writer for shared continuity and product state.
- **Consequences:** High-risk work remains `IMPLEMENTED_NOT_VERIFIED` until a `PASS` report and root reconciliation. `FAIL` or `BLOCKED` prevents dependent work and stage closure; blocking corrections that alter high-risk behavior require follow-up independent review.
- **Affected stages or files:** All Roadmap stages; `AGENTS.md`, `docs/execution/CONTINUITY.md`, every active ExecPlan, and all high-risk product artifacts.
- **Evidence or references:** Explicit user requirement accepted on 2026-09-02; high-risk change gate in `docs/execution/CONTINUITY.md`.

## DEC-013 — Design Missing Pega Artifacts in the Assigned Stages

- **Status:** `ACCEPTED`; the S1 tool-implementation assignment is superseded by DEC-019
- **Context:** No usable exports currently exist for `WriteMemory`, `GetMemory`, the UUID-aware `JsonValidationTool`, or the new Generator agent.
- **Decision:** Treat the missing Generator agent as from-scratch design and implementation work in S3, with S4 completing Validator integration. DEC-019 supersedes only the former assignment to create Memory and UUID-aware validation tool implementations in S1.
- **Reasoning:** The missing Generator remains planned product scope, while the user owns the three external tool implementations and the repository owns their caller-facing contracts.
- **Consequences:** Later Generator and agent-integration ExecPlans must include Pega agent design, export creation, prompt/export parity where applicable, interface tests, and high-risk independent review. S1 must not plan or create the external tool implementations.
- **Affected stages or files:** `S0`, `S1`, `S3`, `S4`; active S0 ExecPlan and future Pega tool and agent artifacts.
- **Evidence or references:** User confirmation on 2026-09-02 that the exports do not exist; DEC-019 and explicit user scope correction on 2026-09-03.

## DEC-014 — Name the New Agent UnitTestGenerator

- **Status:** `ACCEPTED`
- **Context:** The split requires a stable identifier and repository artifact names for the new Generator agent.
- **Decision:** Name the Pega agent rule `UnitTestGenerator`. Use `UnitTestGenerator_Prompt.txt` for its canonical readable prompt and `UnitTestGenerator.txt` for its Pega export; other non-contractual metadata may be selected during S3 implementation.
- **Reasoning:** This applies the user-selected name and follows the repository's existing prompt/export naming convention.
- **Consequences:** S3 validation must verify prompt/export parity and record any implementation-selected Pega metadata.
- **Affected stages or files:** `S0`, `S3`, `S5`; Roadmap, active S0 ExecPlan, and future Generator artifacts.
- **Evidence or references:** User confirmation on 2026-09-02; existing `Main_Agent_Prompt.txt` and `Main_Agent.txt` naming convention.

## DEC-015 — Create the Initial Baseline Commit after S0 Closure

- **Status:** `ACCEPTED`
- **Context:** The repository is on an unborn branch and cannot provide Git-diff evidence until an initial baseline exists.
- **Decision:** The root agent is authorized to create the initial baseline commit after all mandatory S0 acceptance and validation criteria pass, and before S1 work begins.
- **Reasoning:** A verified baseline gives later high-risk refactoring reliable diff evidence without prematurely committing incomplete S0 work.
- **Consequences:** No commit may be created while S0 remains open; S0 closure must be recorded before the commit, and the resulting HEAD must be reconciled into continuity immediately afterward.
- **Affected stages or files:** `S0`, `S1`; all baseline repository files and continuity state.
- **Evidence or references:** User authorization on 2026-09-02.

## DEC-016 — Preserve the Complete Cross-Agent Trace Grammar

- **Status:** `ACCEPTED`
- **Context:** Independent matrix review found that the monolithic Author records Data Page signatures and normalized parameters in SIM trace rows and two Decision Table omission reasons that the current Validator grammar does not recognize.
- **Decision:** The shared ScenarioGroup, Generator, and Validator contract uses the more complete Author grammar. SIM rows retain `sig=<DP_SIG>` and `params=<normalizedParams>`, and Validator compares both against the exact `pySimulation` entry. The allowed OMIT catalog includes `inactive_evaluate_all_scalar` and `inactive_return_values_scalar` in addition to all previously shared reasons.
- **Reasoning:** These fields and reasons encode stable simulation identity and Decision Table semantics; dropping them would violate the accepted instruction-preservation requirement.
- **Consequences:** S2–S4 must keep ScenarioGroup trace grammar, Generator formatting, Validator trace parsing/alignment prose, and regression fixtures synchronized; the omission catalog is not part of the six-field ValidatorReport schema. Discrepancies are blocking high-risk defects.
- **Affected stages or files:** `S0`, `S2`, `S3`, `S4`, `S5`; Instruction Preservation Matrix, Scenario Author and Generator prompts, Validator trace parsing/alignment rules, and regression fixtures.
- **Evidence or references:** `Main_Agent_Prompt.txt` lines 1921, 1952–1961, and 2190–2194; `Validator_Prompt.txt` lines 222, 226–227, and 237; DEC-011; independent matrix audit on 2026-09-03.

## DEC-017 — Keep Main_Agent.txt Reference-Only

- **Status:** `ACCEPTED`
- **Context:** `Main_Agent.txt` is an export of the existing Pega rule, while `Main_Agent_Prompt.txt` contains the canonical readable monolith instructions required for responsibility extraction and preservation.
- **Decision:** Exclude `Main_Agent.txt` from mandatory parity, modification, and refactor deliverables. Use it only as read-only current-state evidence. `Main_Agent_Prompt.txt` is the authoritative source for splitting stable Author instructions. The Validator prompt/export pair remains in scope because Validator refactoring is still required.
- **Reasoning:** The refactor can preserve and partition the current instructions without modifying an unnecessary legacy rule export.
- **Consequences:** S0 records a canonical baseline for `Main_Agent_Prompt.txt` but performs decoded parity only for `Validator_Prompt.txt` and `JsonValidator_tool.txt`. S2 must not edit `Main_Agent.txt`; any future decision to make it a deliverable requires explicit scope change.
- **Affected stages or files:** `S0`, `S2`, `S5`; `Main_Agent_Prompt.txt`, reference-only `Main_Agent.txt`, `Validator_Prompt.txt`, `JsonValidator_tool.txt`, Roadmap, and active ExecPlan.
- **Evidence or references:** User scope clarification on 2026-09-03.

## DEC-018 — Keep Memory Payloads and UUIDs Opaque

- **Status:** `ACCEPTED`
- **Context:** Memory transports materialized ScenarioGroup ledgers and generated UnitTestCandidate JSON between independently executing agents. Transport-layer interpretation or identifier reconstruction would couple Memory to either payload format and could corrupt exact version addressing.
- **Decision:** `WriteMemory` stores `Payload` exactly as supplied without parsing, normalization, schema validation, or restructuring, creates a new immutable record, and returns its generated `UUID`. `GetMemory` returns the stored Payload only for an exact `CaseID`, `Type`, and `UUID` match. Callers treat the returned UUID as an opaque value and pass it unchanged; they never construct, normalize, or infer it.
- **Reasoning:** An opaque transport preserves the Scenario Author's materialized semantic ledger and the Generator's schema-governed candidate verbatim while keeping format validation with the owning agents and Validator.
- **Consequences:** S1 contract fixtures must cover whitespace and special-character preservation as well as cross-case/type/UUID isolation. Memory tools do not validate ScenarioGroup grammar or UnitTestCandidate JSON. UUID representation and Pega storage metadata are implementation details, but observable equality and exact addressing are mandatory. Under DEC-019, Pega runtime proof belongs to the external implementation and is not a repository S1 closure criterion.
- **Affected stages or files:** `S0` through `S5`; Memory tool contracts, Scenario Author, UnitTestGenerator, Validator, Roadmap, and active S0 ExecPlan.
- **Evidence or references:** Explicit user requirement in the architecture discussion that Payload is unstructured and passed as-is and that UUID generation belongs to the Memory tool; DEC-002 through DEC-005.

## DEC-019 — Keep Pega Tool Implementation External and Repository Work Caller-Side

- **Status:** `ACCEPTED`
- **Context:** The user will implement and configure `WriteMemory`, `GetMemory`, and UUID-aware `JsonValidationTool` separately in Pega. Repository work must define how GenAI agents call those tools without attempting to create their backing rules or prove their runtime internals.
- **Decision:** Limit S1 to repository-only design of agent-facing Pega GenAI tool-call contracts: signatures, parameter sources, invocation order, observable response and failure handling, retry prohibitions, UUID propagation, caller ownership, and static contract fixtures. Exclude Rule-AI-Tool and backing-rule implementation, category selection, storage design, exports, ChangeRequests, Pega environment mutation, and runtime behavior verification.
- **Reasoning:** This preserves a precise integration boundary while keeping ownership of Pega implementation with the user and preventing speculative or unusable exports.
- **Consequences:** S1 can close on independently reviewed repository contract evidence without live Pega access. Later runtime integration remains dependent on user-supplied tools conforming to the designed interface; repository work may not claim their persistence, isolation, concurrency, or schema-validation behavior as runtime-verified.
- **Affected stages or files:** `S1` through `S5`; Roadmap, active S1 ExecPlan, continuity state, agent prompts, tool allowlists, and static call-contract fixtures.
- **Evidence or references:** Explicit user direction on 2026-09-03 to keep tool implementation separate in Pega, make repository work responsible only for agent calls to Pega GenAI tools, and use a repository-only path.

## DEC-020 — Close Scenario Complexity Derivation Deterministically

- **Status:** `ACCEPTED`
- **Context:** The canonical Author defines complexity metrics, score, most HIGH conditions, and the presence of confidence/testability caps, but does not quantify `loop+invocation combination requires it` or map tiers to cap values. Leaving either output discretionary would make identical frozen semantics produce different ScenarioGroup records.
- **Decision:** Interpret the loop/invocation HIGH condition conservatively as `loopCount >= 1 AND invocationCount >= 1`, recorded as hard trigger `LOOP_INVOCATION_COMBINATION`. Derive caps exactly as STANDARD=`High/Testable`, ELEVATED=`Medium/Testable`, and HIGH=`Medium/PartiallyTestable`; when `unresolvedCriticalDependencyCount >= 1`, lower the HIGH confidence cap to `Low`. EvidenceSummary gaps and closure rules may lower Scenario confidence/testability further but never raise these caps.
- **Reasoning:** The smallest literal non-zero conjunction preserves the source's independent combination rule without inventing a hidden magnitude. A deterministic monotone cap table removes model discretion while retaining the source rule that complexity changes trace depth rather than assertion coverage.
- **Consequences:** Scenario Author and the S2 checker recompute the combination trigger, tier, and caps from metrics. S3 projects the stored values without reinterpretation. Any later threshold or cap-policy change requires an explicit superseding decision and synchronized fixture update.
- **Affected stages or files:** `S2`, `S3`, `S5`; ScenarioGroup contract, Scenario Author prompt, UnitTestGenerator prompt, fixtures, and deterministic checkers.
- **Evidence or references:** `Main_Agent_Prompt.txt` lines 709–736; second focused S2 design-freeze review on 2026-09-03; DEC-005, DEC-011, and DEC-012.

## DEC-021 — Consolidate Risk-Based Validation and Require the S2 Git Checkpoint

- **Status:** `ACCEPTED`
- **Context:** Repeating independent review after every small checker or documentation edit made S2 slow without proportionate risk reduction. The remaining work is one cohesive responsibility boundary: IPM-AUTH-093–106, ScenarioGroup materialization, legacy persistence removal, and the final handoff. The user also requires the completed verified changes to be committed and pushed.
- **Decision:** Treat the remaining S2 prompt work as one indivisible high-risk batch. Revalidate untouched, previously verified sections by Git diff/hash and cross-cutting invariants rather than repeating clause-by-clause review. After the complete batch passes root checks, run one full independent read-only audit; require follow-up only if corrections change high-risk behavior. After independent `PASS` and S2 closure, the root agent must create the S2 checkpoint commit and push `main` to `origin`.
- **Reasoning:** Cohesive batching preserves deep semantic and cross-section review while removing redundant micro-audits. A verified remote Git checkpoint provides a durable recovery boundary before S3.
- **Consequences:** The complete final batch remains `IMPLEMENTED_NOT_VERIFIED` until independent `PASS`; S3 cannot begin earlier. Low-risk continuity-only corrections do not trigger separate review. Commit and push are explicitly authorized only after S2 closure; any Git or remote failure is reported accurately and must not promote an unpushed state.
- **Affected stages or files:** `S2`, `S3`; `Main_Agent_Prompt.txt`, `docs/contracts/SCENARIO_GROUP_V1.md`, S2 fixtures/checker, Roadmap, active ExecPlan, continuity state, and decision log.
- **Evidence or references:** User approval on 2026-09-04 to optimize validation through larger coherent batches and then create a mandatory commit and push; DEC-012.

## DEC-022 — Pin Independent Repository Reviewer Model Profiles

- **Status:** `SUPERSEDED` by DEC-023 on 2026-09-07; retained as historical policy and review evidence.
- **Context:** Independent validation quality depends on the reviewer model and reasoning effort, but the existing gate did not prescribe either and allowed different sessions to use materially different review strength.
- **Decision:** Spawn routine documentation-only reviewers with `gpt-5.6-terra` and `high` reasoning, high-risk change or batch reviewers with `gpt-5.6-sol` and `xhigh` reasoning, and final whole-stage closure reviewers with `gpt-5.6-sol` and `max` reasoning. Pass both overrides explicitly. These profiles govern repository validation subagents and do not configure the Pega Validator agent. Do not silently substitute an unavailable profile; record the gate as `BLOCKED` and request user direction.
- **Reasoning:** `gpt-5.6-sol` is the available flagship profile for complex professional review, while `xhigh` provides deep default scrutiny and `max` reserves the highest effort for closure-wide audits. `gpt-5.6-terra` provides a proportionate profile for bounded documentation checks.
- **Consequences:** Future ExecPlans and review dispatches must select the profile by review scope. Review reports must state the actual model and effort used. A required review cannot pass when its prescribed profile was not used unless the user explicitly supersedes this decision.
- **Affected stages or files:** `S3`, `S4`, `S5`; `AGENTS.md`, `docs/execution/CONTINUITY.md`, future ExecPlans, and independent review reports.
- **Evidence or references:** User confirmation on 2026-09-04; DEC-012; official OpenAI model documentation for `gpt-5.6-sol` and `gpt-5.6-terra` consulted on 2026-09-04.

## DEC-023 — Use GPT-6 Astra with Extra High Reasoning for Every Repository Reviewer

- **Status:** `ACCEPTED`
- **Context:** The user replaced all three reviewer profiles in DEC-022 with Astra 6 and then specified Extra High reasoning for every profile.
- **Decision:** Use `gpt-6-astra` with `xhigh` reasoning for routine documentation-only reviews, high-risk changes or indivisible batches, and final whole-stage closure audits. Pass both overrides explicitly when spawning every independent repository reviewer. This supersedes all model and reasoning assignments in DEC-022.
- **Reasoning:** Apply the user's selected model and reasoning level consistently across every repository review scope.
- **Consequences:** Preserve the independent read-only review gate, root-only corrections, actual-model/effort reporting, and no-silent-substitution rule. If the required profile is unavailable, record the gate as `BLOCKED` and request user direction. Historical reports retain their actual model names. This policy governs repository validation subagents; it does not change the primary agent or Pega agent configuration.
- **Affected stages or files:** `S3`, `S4`, `S5`; `docs/execution/CONTINUITY.md`, `docs/execution/ROADMAP.md`, future ExecPlans, and independent review dispatches and reports.
- **Evidence or references:** Explicit user instructions on 2026-09-07 to set Astra 6 everywhere in the reviewer table and then use Extra High; the current collaboration tool advertises `gpt-6-astra` with `xhigh` support; DEC-012 and superseded DEC-022.

## DEC-024 — Keep Repository Paths Independent of the Checkout Location

- **Status:** `ACCEPTED`
- **Context:** Continuity and the historical S0 evidence recorded absolute checkout paths from individual machines. The user requested removing these references so the project can be used from another location without a path dependency.
- **Decision:** Describe the repository root as the current Git worktree root and resolve it at runtime with `git rev-parse --show-toplevel` from within the checkout. Use repository-relative artifact paths and document-relative Markdown link targets. Scripts may derive the root from their own location. Do not persist machine-specific checkout prefixes as project configuration or required instructions; summarize historical root-discovery evidence without its absolute path.
- **Reasoning:** The same tracked instructions and links should work after cloning or moving the repository on another machine.
- **Consequences:** Preserve artifact identities, historical verification outcomes, and intentional path strings used as test data. The existing Python checker already derives its root from `__file__` and needs no change. This decision does not fix the separately recorded LF/CRLF validation issue or alter stage status and next action.
- **Affected stages or files:** All future stages and project documentation; `docs/execution/CONTINUITY.md` and `docs/execution/plans/S0-baseline-contracts.md`.
- **Evidence or references:** Explicit user request on 2026-09-07 to remove the fixed Windows and macOS checkout paths; repository search found these prefixes only in continuity and the historical S0 root observation; `scripts/validate_s2_design.py` derives `ROOT` from `Path(__file__).resolve().parents[1]`.

## DEC-025 — Make the S2 Prompt Regression Independent of Checkout Line Endings

- **Status:** `ACCEPTED`
- **Context:** The current LF `Main_Agent_Prompt.txt` is byte-identical to HEAD and reproduces the independently reviewed historical CRLF hash after in-memory conversion, but the S2 checker requires the historical raw bytes and therefore fails on the unchanged checkout.
- **Decision:** For this repository prompt regression only, accept uniform LF or uniform CRLF, replace CRLF with LF in memory, and compare against the fixed reviewed canonical-LF SHA-256 `6F059B641B9CF8B627E6879ED5B7A8FAEE78A616E71E2DD305AF8C051ACD215F`. Retain the 1,973-line guard and verify that re-encoding to CRLF reproduces historical SHA-256 `BACADFB07E90D68B9751B9D573437A21B204E0BCCE87BE6ACE8BD5DDF3CEEC95`. Reject mixed endings, lone CR, BOM, invalid UTF-8, whitespace/content changes, and missing/extra newlines. Do not derive the expected hash from a mutable prompt or rewrite the product file.
- **Reasoning:** Checkout representation is not an instruction change. Canonicalizing only CRLF retains full-content regression and makes the verified baseline usable across machines without relaxing stable semantic checks.
- **Consequences:** The checker reports canonical-LF evidence and runs positive equivalence and negative mutation probes. Historical raw-hash evidence remains historical. ScenarioGroup v1 still requires its own exact LF grammar; Memory Payload and UUID opacity are unchanged. The S3 prerequisite requires independent review before dependent design work.
- **Affected stages or files:** S2 regression and S3 prerequisite; `scripts/validate_s2_design.py`, `docs/execution/CONTINUITY.md`, and `docs/execution/plans/S3-unit-test-generator.md`.
- **Evidence or references:** Root and independent S3 activation review on 2026-09-07 reproduced the original hash failure and LF/CRLF equivalence; the verified S3 plan milestone 2 requires this bounded correction. Independent `/root/review_s2_portability` (`gpt-6-astra`/`xhigh`) confirmed complete LF/CRLF runs, 26 adversarial rejections, fixed hashes, unchanged product/contracts, and continued ScenarioGroup CRLF rejection; focused follow-up returned `PASS` after documentation reconciliation. DEC-018, DEC-023, and DEC-024.

## DEC-026 — Preserve Formal RUT Parameter Types in ScenarioGroup Revision 1.1

- **Status:** `ACCEPTED`; implementation verification is recorded in the active S3 plan.
- **Context:** S3 source inspection confirmed that original Main lines 1554–1565 require formal Pega parameter types, but revision-1 PARAM.valueType and INPUT.mode do not uniquely preserve them. PARAM.dependency=RUT also represents ordinary When input bindings; using it alone would misclassify physical inputs as RUT arguments.
- **Decision:** Add PARAM.formalType and PARAM.formalEvidence in explicit `SG.version=1.1`. Physical Param-namespace INPUT carriers identify actual RUT arguments; exact-name original RuleJSON declaration evidence identifies their formal type. Preserve raw string spelling/case or explicit absence and bind it to a typed EVIDENCE snapshot with source array position. Failed unique-name lookup has array-level evidence with null type. Non-formal input/dependency bindings have neither field populated. Never infer the formal type from a value or property mode.
- **Reasoning:** A declared String and PAGE can hold the same string while requiring different serialized forms; Integer and Decimal also have different admissible values. Explicit provenance preserves the original instruction while keeping semantic acquisition with Scenario Author and formatting with Generator.
- **Consequences:** Old revision 1 and unknown revisions are rejected; rematerialization from original RuleJSON creates new immutable records without relabeling old Payloads or changing Memory Type/tool interfaces. Missing/unknown/unsupported type, incompatible value, or unevidenced PAGE carrier produces a source-addressed projection GAP and prevents Testable/Closed claims. Generator cannot emit that Scenario by dropping the argument or guessing a replacement; its complete scoped-report handling remains S3 design work. All original semantic coverage, expected values, assertions, simulations, and stable IDs are retained. The current prompt digest/line count advance from DEC-025's historical baseline to the reviewed revision, retaining its LF/CRLF-only normalization policy and an executable restoration of the entire prior S2 prompt outside the bounded additions.
- **Affected stages or files:** S3 handoff prerequisite and S5 integration; `Main_Agent_Prompt.txt`, `docs/contracts/SCENARIO_GROUP_V1.md`, S2 implementation slice/fixtures/checker, S3 parameter fixtures/checker/design note, active S3 plan, and continuity.
- **Evidence or references:** IPM-AUTH-035, 072, 078, 088, and 105; original monolith `b9dd565:Main_Agent_Prompt.txt`; `docs/execution/design/S3-parameter-provenance-correction.md`; DEC-001/005/006/011/018/025. No Generator/Validator export, schema, external tool, or Pega environment is changed.

## DEC-027 — Freeze Remaining Source Metadata in a Scenario Profile

- **Status:** `ACCEPTED`; implementation verification is recorded in the active S3 plan.
- **Context:** The S3 source audit found missing concrete carriers for case-key provenance, execution-mode metadata, ordered setup/cleanup actions, property/APB structure and optional context, individual semantic checklist facts, and the final factual wave/seed/Decision Table traces. Generator cannot reacquire these facts or choose new semantics.
- **Decision:** ScenarioGroup revision 1.2 adds one required PROFILE per Scenario with the exact canonical typed data and evidence census defined in the synchronized contract. Preserve all legacy records, counts, coverage, and stable Scenario IDs. New consumers reject older revisions and require fresh immutable rematerialization; the existing revision-1.1 fixtures/checker remain historical/common-core regressions, not a runtime upgrade path. Source profiles store facts only; Pega field assembly stays with Generator.
- **Reasoning:** A complete immutable source permits mechanical projection without hidden semantic reconstruction, lost optional context, invented action ordering, or fabricated checklist/wave history.
- **Consequences:** Model/When execution mode follows the existing false rule; another type needs exact source metadata or an explicit unavailable-mode gap. Action parameters must be source-resolved and projectable. Non-cell assertions remain preserved even when the chosen downstream schema cannot represent them; S3 defines their rejection scope. The bounded prompt-delta checker restores the exact verified DEC-026 prompt before restoring the historical S2 baseline.
- **Affected stages or files:** S3 handoff prerequisite and S5 integration; Main prompt, ScenarioGroup contract, S2 trace slice/checker, sg_profile consumer, S3 profiled fixtures and tests, active plan, source audit, and continuity.
- **Evidence or references:** IPM-AUTH-046/065/067/070/078/088/105; original Main 1387–1493, 1552–1577, 1832–1865, 2202–2203; both existing schema families; DEC-005/006/011/026. On 2026-09-07 the user confirmed target Ruleset/Version selection is already implemented in Pega and is not part of this work: no TargetRuleSet/TargetRuleSetVersion fields or Pega selection implementation are added.

DEC-027 first review on 2026-09-07 returned FAIL. The corrected implementation retains InAnyInstance under original Main 943–984, validates every nested carrier/object, requires separate property/context/action/formal/value acquisition snapshots, and cross-checks final wave/DT/seed traces. Root corrected the residual complete-argument census bypass after the first focused follow-up; final independent gpt-6-astra/xhigh review returned PASS and root reconciled the gate on 2026-09-07.

## DEC-028 — Complete the S3 Projection, Report and Export Interpretations

- **Status:** `ACCEPTED`; complete corrected S3 design VERIFIED after independent gpt-6-astra/xhigh PASS and root reconciliation.
- **Context:** S1 fixes immutable addressing and repair limits, but leaves the complete runtime report, issue coordinates, source rejection and new-agent metadata to S3. Both schemas require target Ruleset/Version while the user explicitly excludes their already-implemented Pega selection from this work.
- **Decision:** Adopt the complete G1–G10 Generator contract and closed consumer report schemas. Validate all ordered sources before projection; malformed/unavailable source is terminal, while a valid but unrepresentable Scenario has an explicit source-local rejection. Shared When context conflicts reject that whole physical group. Apply reports atomically against current indices, use deterministic route precedence and one two-repair budget including pruning, and expose only current validated output in runtime success. Use stable original group-order suffixes for collision-free mechanical rule names. Copy Pega's already-selected schema-required target metadata from its existing UTC template without selecting or configuring a target here; local example values prove formatting only. Preserve all other source authorities and immutable semantic decisions.
- **Reasoning:** Explicit source coordinates and atomic reports prevent stale-index repair, partial silent loss and success attributed to an old UUID. A narrow template metadata carrier honors the user-owned Pega configuration and avoids new inputs or speculative active-version selection. Stable group naming does not change semantic purpose or coverage.
- **Consequences:** S4 must implement the new Validator producer catalog/routes/scopes; current Validator artifacts remain unchanged/incompatible. The export uses observed agent metadata and tool names, with no invented external tool backing categories or runtime-import claim. Missing required template metadata terminates; external template population is not claimed verified. All new interpretations require independent design review before prompt/export creation and independent whole-stage review before closure.
- **Affected stages or files:** S3, S4 and S5; UNIT_TEST_GENERATOR_V1.md, report schemas, S3 matrix/fixtures/oracles, future UnitTestGenerator prompt/export, active plan and continuity.
- **Evidence or references:** S1 sections 3/6/7/9, S3 acceptance criteria, original Main/Validator clauses in the S0 matrix, unchanged candidate schema families, repository-observed Rule-AI-Agent metadata, user clarification on 2026-09-07 that target Ruleset/Version is already implemented in Pega, DEC-006/008/011/019/020/026/027.

## DEC-029 — Preserve Explicit Projection Value and Simulation-Page Provenance

- **Status:** `ACCEPTED`; the cohesive full S3 correction is VERIFIED after focused independent gpt-6-astra/xhigh PASS and root reconciliation.
- **Context:** Independent full-design review found that ASSERT property mode could not distinguish an array from literal array-looking text, and SIM did not explicitly bind its payload to the exact complete page census. Original Main requires both typed expected values and lossless simulation wrappers/pages.
- **Decision:** Require ScenarioGroup revision 1.3 with binding-linked EXECUTION ASSERTION_VALUE snapshots and SIM-linked EXECUTION SIMULATION_BINDING snapshots with exact payloadPage and itemPath (null for page shape). Keep legacy record arities and explicit typed carriers; add payloadPage and itemPath to the full When simulation key. Preserve verified revision-1.2 fixtures as historical. Author rematerializes from original semantic sources; Generator cannot retrofit or infer missing facts. Initialize PAGE arguments through actual INPUT/PARAM links. Preserve exact list wrapper/domain depth and all simulation pages. Complete schema representability after one cached Knowledge batch, reject the narrowest valid source scope before any combined write, and return schema-valid bounded reports for every terminal path.
- **Reasoning:** Explicit source types distinguish null/arrays/strings without changing expected values; binding-aware keys prevent silently merging physically different mocks. Full reverse audits expose dropped optional fields, omitted parameters/actions/pages and invented inputs even when JSON Schema still passes.
- **Consequences:** Current producers and Generator consumers require 1.3; historical 1.2 remains tested without a runtime conversion path. Product creation stays stopped until the full corrected design receives focused independent PASS. Preserve pretty-print preference. Target Ruleset/Version selection remains Pega-owned and unchanged. S4 remains inactive.
- **Affected stages or files:** S3 design and S5 handoff; Main prompt, ScenarioGroup/Generator contracts, source parser, current fixtures, all S3 projection/protocol/audit tests, active plan and continuity.
- **Evidence or references:** Full `/root/review_s3_design` gpt-6-astra/xhigh FAIL and seven P2 findings; original Main 167/2129, 1375–1376, 1554–1565, 1638–1677; IPM-AUTH-063/065/069/078/080/090; DEC-011/016/026–028. Root's complete gate and 55 correction regressions pass locally; this is not an independent or runtime PASS.

DEC-029 final design follow-up returned PASS after root corrected all original and residual findings, including checking final assembled simulation item classes. All seven suites and 66 correction regressions pass; product implementation and whole-stage review remain separately required.

The S3 whole-stage review additionally required the original Main20–24 system-page ban to be executable at the source gate and the original Main709–736 arithmetic/threshold definitions to be self-contained in the runtime source reference. Root clarified these existing requirements in the synchronized Main/ScenarioGroup/Generator contracts without changing source arity, metric ownership or recorded semantics. Bounded restoration retains the exact reviewed1.3 prompt; focused closure review remains pending at this checkpoint.

S3 closure on 2026-09-07: independent `/root/review_s3_closure` used gpt-6-astra/xhigh and returned focused whole-stage PASS for all15criteria. Root reconciled every finding and the complete static evidence; DEC-026–029 implementations and S3 artifacts are VERIFIED. The original-clause source-gate/complexity clarifications and metadata/checker portability corrections are included. S4 remains NOT_STARTED; S3 work was uncommitted at the 2026-09-07 closure and Pega import/runtime remain external.

On 2026-09-08 the user-authorized local S3 checkpoint was created with `vkoloskov <95134563+vkoloskov@users.noreply.github.com>` as both author and committer. It includes the verified bounded pre-commit hygiene/census corrections and this reconciliation; resolve its final self-referential hash from Git. Parent: `8509a508ee586136b4a06caa86ee50a51a391b0e`. No push or S4 activation was performed.

## DEC-030 — Define Candidate-only Validator Evidence and Bounded Diagnostics

- **Status:** ACCEPTED and VERIFIED implementation after final S4 whole-stage gpt-6-astra/xhigh PASS and root reconciliation; S4 CLOSED on 2026-09-08.
- **Context:** S1/S3 restrict Validator to the candidate UUID and three read-only interfaces. Existing pySimulation schemas contain no separate DP sig/params or payloadPage/itemPath carriers, and the canonical trace does not repeat every typed source fact. Legacy prose also leaves oversized schema diagnostics and unavailable Knowledge handling underdetermined.
- **Decision:** Preserve the full DEC-016 trace and compare exact sig/params in unique physical mock associations and across shared When Scenarios; Generator alone verifies those facts against immutable source ledgers. Do not invent DP parameter fields or compare them to unrelated RUT arguments, select an unevidenced collection, coerce unquoted text into typed values, or claim source proofs absent from candidate JSON. Validator still detects every observable mismatch and never weakens Generator's source audit. Define oversized schema diagnostics as over 2,000 characters alongside the existing 25-error and explicit broad-container indicators; use bounded summaries. Unavailable UTC guidance produces existing AMBIGUOUS/HUMAN_REVIEW after schema success. Parsing an unreadable allegedly schema-passed candidate is a MEMORY_READ_TOOL_ERROR transport-consistency failure, not a second schema verdict.
- **Reasoning:** The accepted candidate-only interface cannot independently reconstruct facts deliberately omitted from candidate schemas. Explicit evidence limits preserve honest role ownership and deterministic terminal reports while keeping schema/transport contracts unchanged.
- **Consequences:** This clarifies the feasible candidate-side portion of DEC-016 without changing its grammar or the Generator's source comparison. Missing/contradictory final decisions remain semantic rejection; uncertainty does not create new semantics. Report schema/catalog, source revision, Author/Generator products and target Pega configuration remain unchanged. Independent design review must verify the preservation boundary before product changes.
- **Affected stages or files:** S4 producer contract, instruction slice, protocol/alignment fixtures, Validator prompt/export and S5 integration evidence.
- **Evidence or references:** S1 sections 7–9; S3 G5/G7/G8; IPM-VAL-022/024/043; current candidate schema Simulation definitions and scripts/generator_projection.py simulations(); DEC-007/016/018/019/028–029; original Validator 158–178 and 198–204.

DEC-030 first S4 design review returned FAIL on 2026-09-08. Root corrected seven P2 groups before product creation: final ASSERT/OMIT/value contradictions, exact-first quote/path comparison, observable assertion/When context, parameterized mock input/setup roots, explicit mass-error forms/nested containers, and pre-Knowledge traversal guards. The absent-source limitation does not exempt any observable comparison. Focused independent verification remains required.

DEC-030 final design follow-up received independent gpt-6-astra/xhigh PASS after all original and residual findings were corrected. All 33 producer groups and seven S3 suites pass; product synchronization and whole-stage closure remain separately required.

DEC-030 whole-stage review returned FAIL on two original-clause gaps: explicit Text/TrueFalse behavior must precede physical matching and normalization, and blank RUTType must stop before tools. Root corrected both without expanding absent-source type inference, changing opaque addresses or modifying S1/S3. The 35-group local producer suite passes; focused whole-stage review remains required.

Focused whole-stage review confirmed the original corrections and identified the supported String mode missing from the string constraint list. Root added it and independent explicit eight-mode schema-valid controls. No source, schema or ownership boundary changed; focused PASS remains pending.

S4 closure on 2026-09-08: final focused /root/review_s4_closure used actual gpt-6-astra/xhigh and returned PASS with all original/residual findings closed and all 14 criteria ready. Root reconciled 35 producer groups, 76 additional independent scalar probes, five blank-RUT controls, all seven S3 suites/180 corrections, 150/73 dispositions, 57 protected artifacts, exact artifact hashes/parity and bounded export restoration. DEC-030 implementation and the Validator product pair are VERIFIED; S4 is CLOSED. S5 remains NOT_STARTED. No S4 commit/push or Pega import/runtime was performed.

On 2026-09-08 the user-authorized local S4 closure checkpoint was created in 20 project paths with vkoloskov <95134563+vkoloskov@users.noreply.github.com> as both author and committer. The complete staged S4 gate passed. This same checkpoint contains its reconciliation; resolve its final self-referential hash from Git. Parent is 4393c680633d176129676f7b91179262cc25391f. No push or S5 activation was performed; .idea/ remains excluded.

## DEC-031 — Reconcile S5 Runtime Envelopes and Preserve Historical Evidence

- **Status:** ACCEPTED and VERIFIED implementation after independent S5 whole-stage gpt-6-astra/xhigh PASS and root reconciliation; S5 CLOSED on2026-09-08.
- **Context:** S1 permits platform metadata but Main Section1A and protected SCENARIO_GROUP_V1.md:17 historically reject all extra WriteMemory fields. Main/Generator embedded SIM prose also predates DEC-030's explicit candidate evidence boundary. Effective prompts retain obsolete transport names in prohibitions/overridden historical context.
- **Decision:** Supersede only the historical envelope extra-field rejection with S1's required-field semantics, retaining exact names/types/error rules and no retries/partial handoff. The protected ScenarioGroup file remains historical evidence; S5_INTEGRATION.md and effective Author instructions govern that one envelope discrepancy without changing payload grammar. Propagate DEC-030 into bounded Main/Generator runtime source references. Remove literal obsolete transport names while preserving prohibitions and overridden semantic/downstream ownership. Add the unchanged full GeneratorRunReport schema as Author's terminal response reference; preserve the fixed two-field external mapping.
- **Reasoning:** The final pipeline must accept valid external tool envelopes consistently and cannot ask Validator to prove fields absent from its candidate. Explicit current overlays prevent weakening source grammar or silently rewriting verified historical evidence.
- **Consequences:** Exact old/new replacements, original row traces and all protected baseline hashes require independent design and whole-stage review. Historical S2/S3/S4 gates run on an isolated fixed S4 checkout; current artifacts and connected actual oracles receive separate checks. No external Pega implementation, schema/report/source revision or target selection changes.
- **Affected stages or files:** S5 integration contract, reverse matrix, static Author boundary/test harness, Main/Generator prompt overlays and Generator export; global continuity.
- **Evidence or references:** S1§5, Main§1A, SCENARIO_GROUP_V1.md:17, DEC-016/030, fixed S4 checkpoint d4061046650c87b9da2c4f87141f23aa2602f082; independent activation review explicitly identified the historical source-envelope clause.

DEC-031 first S5 design review returned FAIL on three P2 groups: the executable embedded Section13 repeated the metadata rejection, the reverse audit omitted current consumer checks and accepted invalid destinations, and schema-valid G9 contradictions became external success. Root corrected the bounded Section13 clause, recorded36explicit current-role additions with exact prompt evidence and destination/Markdown negative checks, and added report-only G9 consistency/known handoff checks plus13schema-valid adversarial controls. Required fields, historical files and fixed outer response remain unchanged; no candidate read or independent proof of Validator execution is introduced. Focused independent design PASS is required before products.

DEC-031 focused independent S5 design review returned PASS on all three corrections. Complete current and fixed historical gates plus18additional schema-valid multi-group report probes passed. Root reconciled the unchanged product baseline and authorizes the reviewed overlay within the selected stage; whole-stage PASS remains required before closure.

S5 closure on2026-09-08: /root/review_s5_closure actual gpt-6-astra/xhigh returned whole-stage PASS with no actionable findings and all13criteria ready. Root reconciled16integration groups,150rows/36current checks,85protected artifacts, eight artifact/four matrix mutations, both-pair parity, exact product hashes and fixed historical S4/S3 PASS, plus five independent additional probes. DEC-031 implementation and the repository refactor are VERIFIED; S0–S5 are CLOSED. S5 changes remain uncommitted, with no push or Pega import/runtime performed.

On 2026-09-08 the user-authorized local S5 closure checkpoint was created in 22 project paths with vkoloskov <95134563+vkoloskov@users.noreply.github.com> as both author and committer. The complete staged S5 gate passed. This same checkpoint includes Git-state reconciliation; resolve its final self-referential hash from Git. Parent is d4061046650c87b9da2c4f87141f23aa2602f082. All S0–S5 remain CLOSED; no push or Pega runtime was performed and .idea/ remains excluded.

## DEC-032 — Keep Repository Traceability Outside Runtime Prompts

- **Status:** ACCEPTED and VERIFIED for both IPM and user-clarified DEC cleanup after independent gpt-6-astra/xhigh PASS and root reconciliation on2026-09-08.
- **Context:** The user requested removing labels such as `[IPM-AUTH-001, IPM-AUTH-002]` and asked why they appear in prompts. These labels are Instruction Preservation Matrix references for repository audits, not operational agent instructions.
- **Decision:** Remove repository IPM and DEC references from effective canonical prompts, including inline annotations and prose attribution. Preserve the full operative requirements; use explicit existing revision/contract subjects when necessary for grammatical sentences. Synchronize both affected exports only inside pySystemPrompt. Keep matrix and decision IDs in documentation/fixtures and use exact section headings plus external instruction quotes for runtime traceability. The user clarification supersedes the previous IPM-only retention of DEC labels.
- **Reasoning:** Repository traceability must remain verifiable without exposing audit labels to the Pega agents. This removes annotation noise while retaining the original obligations.
- **Consequences:** Retain the verified27IPM replacements, then remove25DEC references through16closed editorial substitutions across all three canonical prompts. Preserve all106Author IDs via132external section/quote anchors, update hashes and synchronize both paired exports only inside pySystemPrompt. All83other baseline artifacts remain fixed; all five products are exactly reconstructed from the fixed S5 closure plus the authorized cleanup. Require the full gate and independent gpt-6-astra/xhigh review. No semantic, route, schema, source, tool or target-selection change is authorized. Main_Agent.txt remains reference-only and byte-identical.
- **Affected stages or files:** S5 post-closure cleanup addenda; Main/Generator/Validator canonical prompts and both Generator/Validator exports; S5 builder/checker, annotation/anchor fixtures, reverse matrix, artifact/preservation manifests and continuity.
- **Evidence or references:** User request on2026-09-08; initial S5 closure2c2fc195cc97ba5ab45efa6dcb90b5cdd688737a; fixtures/s5/prompt-annotation-deltas.json and fixtures/s5/author-instruction-anchors.json. The separate two P2 Validator findings remain outside this change.

DEC-032 first independent review returned FAIL with two P2 findings despite annotation-only current products and full local/independent gate PASS. Root corrected the catalog gate with a closed annotation replacement allowlist and fixed pre-cleanup closure-byte check, added three normative insertion/deletion/closure-drift controls, and reconciled current HEAD/origin tracking0/0 without attributing the external update. Focused independent PASS remains required.

DEC-032 focused independent /root/review_ipm_cleanup actual gpt-6-astra/xhigh returned PASS: both first-review findings are closed, the original injection plus six additional attacks are rejected, current Git tracking is reconciled, product bytes remain the annotation-only reviewed versions, and the complete corrected current/historical gate passes. Root reconciled this evidence and closed annotation cleanup criterion14; changes remain uncommitted. No Pega runtime or fixes to the two separate Validator findings are claimed.

DEC-032 user clarification on2026-09-08 explicitly identifies remaining [DEC-026] as unwanted. IMPLEMENTED_NOT_VERIFIED — the user clarified that remaining DEC references such as [DEC-026] must also be removed. Root removed25references (Main10, Generator12, Validator3) using16closed editorial substitutions that preserve operative requirements. Both exports are synchronized only inside pySystemPrompt. All five pre-cleanup products remain pinned to2c2fc19, current hashes/Author anchors are updated, and83other baseline files remain fixed; the Validator pair is now an explicitly authorized annotation-only delta. Full local validation and independent gpt-6-astra/xhigh review are pending. No commit/push, Pega runtime or unrelated Validator behavior fix is included. The DEC-only delta is25references using16fixed editorial substitutions after the unchanged verified IPM cleanup.

DEC-032 clarified DEC cleanup received independent /root/review_ipm_cleanup actual gpt-6-astra/xhigh PASS with no remaining findings. Root corrected the reviewer-reported current-scope documentation, reconciled the complete gate,25DEC references/16substitutions, both export metadata/parity checks,83protected files and full external traceability, and closed criterion15. All cleanup changes remain uncommitted; no Pega runtime or unrelated Validator fix is claimed.

VERIFIED — on2026-09-08 root created the user-authorized cleanup commit f9d88f3d6c2a9b98849bcfef03d2657503bf77ab (`chore: remove audit references from agent prompts`) in19project paths, parent2c2fc195cc97ba5ab45efa6dcb90b5cdd688737a, with vkoloskov <95134563+vkoloskov@users.noreply.github.com> as author and committer. The complete staged S5 gate passed, including16integration groups,150rows,83protected artifacts and the fixed historical S4/S3 suite. .idea/ was excluded. Local origin/main was subsequently observed at the same cleanup commit; this task issued no fetch/push command and does not attribute that ref update. This separate documentation checkpoint records completion without rewriting the cleanup commit. Criteria1–15 remain CLOSED; the two separate Validator findings remain unfixed.

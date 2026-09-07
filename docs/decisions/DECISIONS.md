# Decision Log

This is an append-oriented log. Add accepted durable decisions; do not record unresolved ideas as decisions. Supersede prior entries explicitly instead of rewriting their historical meaning.

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

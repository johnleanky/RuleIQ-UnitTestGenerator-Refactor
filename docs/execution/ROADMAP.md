# Unit Test Generator Refactor Roadmap

This roadmap records progress stages only. Detailed execution instructions belong in the active ExecPlan referenced by `CONTINUITY.md`.

Every stage is governed by the Instruction Preservation Matrix and the high-risk change gate in `CONTINUITY.md`. A high-risk change remains `IMPLEMENTED_NOT_VERIFIED` until an independent read-only subagent reports `PASS` and the root agent reconciles the evidence and corrections.

## S0 — Baseline and Contract Stabilization

- **Objective:** Establish a verified repository baseline, complete instruction-preservation traceability, valid schema fixtures, canonical-prompt integrity and in-scope Validator prompt/export checks, and durable target-architecture contracts before product refactoring.
- **Dependencies:** None.
- **Status:** `CLOSED`
- **Mandatory acceptance criteria:**
  - The five-file continuity framework exists and passes its initialization checks.
  - Both schema and example families parse as JSON, and each example is validated against its matching schema using available tooling.
  - The canonical `Main_Agent_Prompt.txt` baseline is recorded without requiring parity to `Main_Agent.txt`, and decoded Validator prompt/export baseline results are recorded.
  - The Instruction Preservation Matrix accounts for every normative section and cross-cutting contract in `Main_Agent_Prompt.txt` and every affected Validator contract.
  - Every matrix row records classification, destination owner, migration action, target location, regression evidence, and status; no stable instruction is removed without an accepted decision.
  - Accepted Memory, ScenarioGroup, Generator, Validator, and failure-handling contracts, including the required from-scratch Pega artifact designs, are sufficiently explicit to begin S1.
  - An independent read-only validator reports no blocking defects.
- **Required validation:** Continuity consistency checks, 100% Instruction Preservation Matrix coverage, BOM-aware JSON parsing, schema/example validation, canonical Main prompt integrity, Validator prompt/export boundary and decoded-equivalence checks, and independent read-only review.
- **Unresolved questions:** None. Both example families passed the accepted two-implementation local fallback; absence of an installed complete Draft 2020-12 or runnable Pega validator remains a recorded tooling limitation, not unresolved mandatory validation.

## S1 — Pega Memory Transport

- **Objective:** Provide immutable UUID-addressed `WriteMemory` and `GetMemory` records and make `JsonValidationTool` validate an exact `UnitTestCandidate` UUID.
- **Dependencies:** `S0`
- **Status:** `NOT_STARTED`
- **Mandatory acceptance criteria:**
  - Because no usable exports exist, the `WriteMemory`, `GetMemory`, and UUID-aware `JsonValidationTool` Pega rules and exports are designed and created from the accepted contracts.
  - `WriteMemory(CaseID, Type, Payload)` creates an immutable record and returns a UUID.
  - `GetMemory(CaseID, Type, UUID)` reads only the exact matching record and never falls back to the latest record.
  - Memory treats Payload and generated UUID values as opaque: Payload round-trips unchanged, and callers pass returned UUIDs unchanged.
  - Supported v1 types are `ScenarioGroup` and `UnitTestCandidate`.
  - `JsonValidationTool(CaseID, UUID, JsonSchema)` validates the exact candidate version.
  - Failure responses and no-retry behavior are explicit and tested.
- **Required validation:** Exact Payload create/read round trips including whitespace and special characters, cross-case/type/UUID isolation, multiple candidate versions for one case, failure behavior, and a high-risk-gate independent review after interface or tool changes.
- **Unresolved questions:** None; artifact design and creation are stage work.

## S2 — Scenario Author Extraction

- **Objective:** Restrict the existing main agent to semantic analysis, final scenario formation, grouping, materialization, and one Generator handoff.
- **Dependencies:** `S1`
- **Status:** `NOT_STARTED`
- **Mandatory acceptance criteria:**
  - Scenario Author owns RUT/dependency analysis, coverage, inputs, simulations, assertions, omissions, and final semantic audit.
  - Each physical unit-test group is stored as one immutable `ScenarioGroup` record.
  - Non-When groups contain one scenario; Rule-Obj-When groups are homogeneous by `SIMULATION_GROUP_KEY`.
  - Scenario Author does not create RuleCode, serialize UnitTestRules, run schema repair, or invoke Validator directly.
  - Legacy `MemoryTemp` and response-record persistence are absent from the Scenario Author workflow.
  - Every Scenario Author-owned Instruction Preservation Matrix row is implemented at its designated destination and retains its stable behavior.
  - Each split, replacement, or removal is traceable to its source instruction, accepted decision, and regression evidence.
- **Required validation:** Matrix-row traceability, responsibility-boundary review, ScenarioGroup ledger audit, grouping cases, canonical prompt integrity, regression checks for preserved semantic behavior, and high-risk-gate independent review after each prompt split or legacy removal batch. `Main_Agent.txt` is not an S2 parity or edit target.
- **Unresolved questions:** None beyond S1 tool availability.

## S3 — Unit Test Generator

- **Objective:** Design and add one sequential Pega agent named `UnitTestGenerator` that reads ordered ScenarioGroup UUIDs, creates one combined candidate, performs projection-only repair, and returns a runtime report.
- **Dependencies:** `S1`, `S2`
- **Status:** `NOT_STARTED`
- **Mandatory acceptance criteria:**
  - The new rule is named `UnitTestGenerator`; its canonical readable prompt is `UnitTestGenerator_Prompt.txt` and its Pega export is `UnitTestGenerator.txt`.
  - Generator consumes `CaseID`, immutable `RUTType`, and ordered `ScenarioGroupUUIDs`.
  - It creates one UnitTestRules entry per group and one combined `UnitTestCandidate` record.
  - It performs no RUT/dependency semantic analysis and does not change expected values, coverage, assertions, or simulations.
  - Repairs create new candidate UUIDs and Validator always receives the current UUID.
  - Scenario-local failures, shared When-group failures, and candidate-wide failures follow the accepted scope rules.
  - `GeneratorRunReport` returns `Completed`, `PartiallyCompleted`, or `Failed` consistently.
  - Every Generator-owned or shared Instruction Preservation Matrix row is implemented without duplicating semantic ownership from Scenario Author.
- **Required validation:** Matrix-row traceability, standard and When grouping fixtures, multiple simulation groups, ordering, immutable semantic input, repair-version addressing, failure pruning, runtime-report checks, and high-risk-gate independent review after each prompt or interface batch.
- **Unresolved questions:** None; non-contractual Pega metadata may be selected during implementation and must be recorded and validated in the S3 ExecPlan.

## S4 — Validator Refactor

- **Objective:** Validate UUID-addressed candidates and separate projection repair from immutable semantic rejection.
- **Dependencies:** `S1`, `S3`
- **Status:** `NOT_STARTED`
- **Mandatory acceptance criteria:**
  - Validator accepts `CaseID`, immutable `RUTType`, and candidate UUID.
  - Validator and JsonValidationTool read the same exact candidate record.
  - Routes are `OK`, `GENERATOR_REPAIR`, `SEMANTIC_REJECT`, and `HUMAN` with deterministic precedence.
  - Issue unit/scenario indices identify scenario, group, or candidate scope.
  - Existing schema, AssertionDecisionTrace-to-RuleCode, MultInpComb, and documentation checks remain effective.
  - Validator never mutates Memory or returns rewritten UnitTestRules.
  - Every Validator-owned Instruction Preservation Matrix row is retained or changed only by an explicit accepted decision with regression evidence.
- **Required validation:** Matrix-row traceability, route precedence, schema-invalid short circuit, malformed tool responses, alignment checks, issue scoping, shared-group rejection, prompt/export parity, and high-risk-gate independent review after each prompt or route batch.
- **Unresolved questions:** None beyond S1 and S3 artifacts.

## S5 — Integration and Legacy Cleanup

- **Objective:** Integrate the three-agent flow, remove legacy transport references, and prove end-to-end behavior without unintended export changes.
- **Dependencies:** `S2`, `S3`, `S4`
- **Status:** `NOT_STARTED`
- **Mandatory acceptance criteria:**
  - Each agent exposes only its intended tools and responsibilities.
  - Legacy `MemoryTemp`, `CreateAIAgentResponseRecord`, and `GetAIAgentResponseRecord` references are absent.
  - Every prompt/export pair explicitly selected as an implementation deliverable is synchronized after decoding. `Main_Agent.txt` remains excluded and reference-only under DEC-017.
  - A reverse matrix audit proves that every stable source instruction has exactly one effective owner, no required invariant is orphaned, and no conflicting duplicate survives across agents.
  - Only instructions classified as obsolete legacy behavior and linked to accepted decisions are removed.
  - Standard, When, partial-success, shared-group failure, all-failed, wrong-UUID, and repair-version flows pass.
  - Scenario Author maps Generator `Completed` and `PartiallyCompleted` to the existing external `Completed` status and maps Generator `Failed` to external `Failed`.
  - An independent end-to-end validator reports no blocking defects.
- **Required validation:** Reverse Instruction Preservation Matrix audit, repository-wide legacy search, preserved-behavior regression suite, schema validation of final candidates, full flow fixtures, parity and targeted diffs only for selected deliverable exports, explicit confirmation that `Main_Agent.txt` stayed untouched, and an independent end-to-end review after final integration.
- **Unresolved questions:** None; any newly discovered integration dependency must be recorded before execution.

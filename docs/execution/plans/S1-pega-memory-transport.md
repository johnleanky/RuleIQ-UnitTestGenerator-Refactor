# ExecPlan: S1 Pega GenAI Tool Invocation Contracts

- **Roadmap stage:** `S1`
- **Plan status:** `CLOSED`
- **Last reconciled:** 2026-09-03

## Purpose

Design and independently verify the repository-owned integration contract by which the Scenario Author, Unit Test Generator, and Validator call user-implemented Pega GenAI tools for immutable UUID-addressed Memory transport and exact candidate validation.

## Scope

- Define the caller-visible signatures for `WriteMemory(CaseID, Type, Payload)`, `GetMemory(CaseID, Type, UUID)`, and `JsonValidationTool(CaseID, UUID, JsonSchema)`.
- Map every input parameter to its agent-owned source and every returned field to the caller action that consumes it.
- Define which agent may call each tool and the permitted call order across Scenario Author, Unit Test Generator, and Validator flows.
- Specify observable success, schema-invalid, not-found, address-mismatch, malformed-response, and execution-failure handling.
- Preserve opaque Payload and UUID forwarding, exact addressing, fixed v1 Type values, immutable-version semantics, and no-latest/no-automatic-retry rules at the caller boundary.
- Create repository-only static call fixtures, response fixtures, and sequence traces suitable for later prompt implementation and external Pega conformance checks.
- Apply the high-risk independent-validation gate to the completed call-contract design before dependent prompt work begins.

## Excluded Scope

- Creating or modifying Pega `Rule-AI-Tool` rules, backing Activities or other backing rules, storage classes/tables, UUID generation, or schema-validation implementation.
- Selecting backing categories, rulesets, classes, rule identifiers, storage representation, export filenames, or other Pega implementation metadata.
- Creating Pega exports, ChangeRequests, deployments, or mutations in any Pega environment.
- Claiming runtime verification of persistence, immutability, isolation, concurrency, UUID generation, schema execution, or importability.
- Scenario Author prompt extraction, which belongs to S2.
- `UnitTestGenerator` prompt and agent-export creation, which belongs to S3.
- Validator prompt/export refactoring, which belongs to S4.
- Repository artifact integration and legacy cleanup belong to S5; live Pega runtime integration and conformance remain external and user-owned under DEC-019.
- Modification, parity enforcement, or repurposing of reference-only `Main_Agent.txt`.

## Assumptions and Unknowns

- S0 is closed and baseline commit `99e038330076288bcc86bcc556681dc3efc82c74` is the comparison authority.
- DEC-002, DEC-003, DEC-007, DEC-018, and DEC-019 are the fixed S1 interface boundary; DEC-019 supersedes DEC-013's repository implementation assignment for these tools.
- The user owns separate Pega implementation and configuration of the three tools, including backing categories and rules.
- Repository work is intentionally limited to caller-side design and static verification.
- Exact Type values are `ScenarioGroup` and `UnitTestCandidate`; CaseID, Payload, and returned UUID values are passed unchanged.
- `UNKNOWN` and external to S1 — exact Pega implementation metadata and runtime behavior until the user supplies conforming tools or runtime evidence.
- The minimum observable response fields beyond the already accepted UUID, `IsValid`, and `ValidationMessage` outputs must be fixed by the S1 call-contract design without prescribing backing implementation.

## Dependencies

- Closed S0 and its verified Instruction Preservation Matrix.
- Accepted decisions in `docs/decisions/DECISIONS.md`, especially DEC-019.
- Current caller behavior in `Main_Agent_Prompt.txt`, `Validator_Prompt.txt`, and `JsonValidator_tool.txt` as read-only source evidence.
- Both existing JSON schema families for static candidate-call fixtures.
- Independent read-only subagent availability for the high-risk design gate.

## Milestones

1. Reconcile S1 scope, Roadmap, decisions, and continuity with the user-owned Pega implementation boundary.
2. Draft one repository call-contract specification for all three tools, including signatures and observable envelopes.
3. Map caller ownership, parameter provenance, invocation order, UUID propagation, and failure actions across the three agents.
4. Add static nominal, isolation, versioning, opaque-data, malformed-response, failure, and no-retry fixtures and sequence traces.
5. Run repository consistency, traceability, and scope validation.
6. Obtain an independent read-only `PASS` on the complete high-risk interface design and reconcile any findings before S1 closure.

## Progress

- `VERIFIED` — S0 closed after full independent audit and focused follow-up `PASS`.
- `VERIFIED` — baseline commit `99e038330076288bcc86bcc556681dc3efc82c74` exists and the working tree was clean immediately after creation.
- `VERIFIED` — immutable exact-address, opaque Payload/UUID, Validator UUID, and failure-boundary decisions are recorded.
- `VERIFIED` — the user assigned Pega tool implementation and configuration to themselves, selected a repository-only path, and limited repository work to the agents' Pega GenAI tool-call design.
- `VERIFIED` — DEC-019 and the revised planning artifacts record the new ownership boundary; independent read-only review returned `PASS` after two residual scope statements were corrected.
- `PARTIAL` — static baseline discovery identified the current Validator call and legacy CaseID-only read behavior; live Pega discovery timed out, but it is no longer required for S1.
- `VERIFIED` — consolidated caller-side contract specification and F01–F13 static fixtures exist at `docs/contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md`; after correction of every first-review finding, focused independent follow-up returned `PASS`.
- `VERIFIED` — independent high-risk review of the S1 scope revision returned `PASS`.
- `VERIFIED` — the first independent caller-contract review returned `FAIL`; root corrections made error codes disjoint, completed the Memory-read ValidatorReport, restored mass-error compaction, added DEC-008 result mapping, and removed stale continuity state. Focused follow-up returned `PASS` with only bookkeeping updates requested during root reconciliation.
- `VERIFIED` — root static validation found 13 parseable JSON examples, exactly F01–F13, no unresolved IPM references, synchronized exact-next-action text, zero product changes, and no `git diff --check` errors.

## Discovery Record

- `VERIFIED` — baseline HEAD `99e038330076288bcc86bcc556681dc3efc82c74` remains the product comparison authority; all product files match it at S1 scope reconciliation.
- `VERIFIED` — `JsonValidator_tool.txt` identifies current Activity-backed GenAI tool references but omits complete parameter mappings; S1 needs caller-visible behavior only, not backing metadata.
- `VERIFIED` — the current Validator invokes `JsonValidationTool(CaseID, JsonSchema)`, expects boolean `IsValid` and `ValidationMessage`, and later reads candidate JSON by CaseID. The target contract adds UUID to validation and requires exact `GetMemory(CaseID, UnitTestCandidate, UUID)` in S4.
- `VERIFIED` — no standalone tool or backing-rule export exists in the repository; DEC-019 makes their creation explicitly external and out of scope.
- `VERIFIED` — earlier live Pega application and rule-list calls timed out after 120 seconds. This remains historical discovery evidence but does not block repository-only contract design.

## Acceptance Criteria

- One repository specification defines all three tool signatures, allowed callers, parameter provenance, invocation order, minimum observable response fields, failure classes, and caller actions.
- The `WriteMemory` caller contract requires CaseID, exact Type, and opaque Payload; consumes exactly one returned opaque UUID for a successful write; treats failed or malformed responses as terminal; and forbids automatic retry without a future accepted idempotency contract.
- The `GetMemory` caller contract requires CaseID, exact Type, and opaque UUID; accepts only the exact matching Payload; treats missing or mismatched addresses as failures; and forbids latest-record fallback.
- Only exact v1 Type values `ScenarioGroup` and `UnitTestCandidate` appear in valid calls.
- Multiple record and repair-version UUIDs remain distinct in all call traces; callers never reconstruct, normalize, infer, or silently replace a UUID.
- The `JsonValidationTool` caller contract requires CaseID, current candidate UUID, and JsonSchema; targets exact Type `UnitTestCandidate`; consumes boolean `IsValid` plus `ValidationMessage`; and distinguishes execution or malformed-response failure from schema-invalid content.
- Caller traces cover Scenario Author group writes and Generator handoff, Generator exact group reads and candidate writes, and Validator/current-candidate exact validation and read behavior.
- Static fixtures cover special-character Payloads, wrong CaseID/Type/UUID, unknown UUID, repeated writes, multiple candidate versions, no-latest behavior, schema-invalid content, malformed responses, and tool failures.
- No Pega implementation artifact, export, backing category, backing rule, storage design, ChangeRequest, deployment, or runtime verification claim is created as an S1 deliverable.
- The completed design receives an independent read-only `PASS`, and the root agent reconciles the report before S1 closure or dependent prompt implementation.

## Validation

- Use `git diff --check`, named-file diffs, status, and baseline hashes to prove repository scope against HEAD `99e038330076288bcc86bcc556681dc3efc82c74`.
- Check the contract specification against DEC-002, DEC-003, DEC-007, DEC-018, and DEC-019 and the relevant Instruction Preservation Matrix rows.
- Verify exact tool names, parameter order/names, Type literals, UUID provenance, response handling, no-latest behavior, and no-automatic-retry behavior across every static trace.
- Verify every response field has one defined meaning and every failure class has a deterministic caller action.
- Search the S1 deliverables for prohibited backing implementation, export creation, storage design, ChangeRequest, deployment, or runtime-verification claims.
- Treat fixtures as contract examples only; do not promote static evidence to Pega runtime evidence.
- Provide the independent validator with the changed decisions and planning artifacts, fixed contracts, relevant matrix rows, final specification and fixtures, baseline diff, commands, and acceptance criteria.
- At stage closure, re-run link, decision, Roadmap, continuity, exact-next-action, product-scope, and independent-review checks.

## Evidence

- `VERIFIED` — S0 final independent audit and focused follow-up found no remaining blocker in the fixed caller-facing contracts.
- `VERIFIED` — DEC-018 requires unchanged opaque Payload storage/retrieval and unchanged opaque UUID forwarding.
- `VERIFIED` — DEC-019 makes Pega tool implementation user-owned and limits repository S1 work to caller-side design and static fixtures; independent read-only scope review returned `PASS`.
- `VERIFIED` — initial baseline commit `99e038330076288bcc86bcc556681dc3efc82c74` contains all 20 baseline files and precedes S1 activation.
- `VERIFIED` — the consolidated contract specification and F01–F13 fixtures passed focused independent follow-up and root reconciliation after all first-review defects were corrected.

## Risks

- A caller contract can accidentally prescribe backing implementation details. Keep requirements observable at the tool boundary and mark internals external.
- Ambiguous response envelopes can cause agents to confuse tool failure with business-invalid content. Define minimum fields and deterministic branching for every result class.
- XML/HTML or prompt serialization can mutate opaque Payload content. Static fixtures must include boundary whitespace and encoding-sensitive characters for later prompt regression checks.
- Automatic retries can duplicate immutable writes. Every caller path must make a failed write terminal unless a later decision introduces idempotency.
- A CaseID-only or latest-record fallback would invalidate independent Generator runs and repair-version validation. Every valid trace must preserve the exact tuple and current UUID.
- JsonValidationTool and GetMemory can accidentally target different candidate versions. Validator traces must propagate the same current candidate UUID unchanged to both calls.
- The interface design is high-risk; its first independent review returned `FAIL`, and it became `VERIFIED` only after root correction, focused independent `PASS`, and root reconciliation.

## Exact Next Action

Select S2 as the next active Roadmap stage and create its ExecPlan before changing Scenario Author product artifacts.

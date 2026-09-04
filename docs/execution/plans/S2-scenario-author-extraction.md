# ExecPlan: S2 Scenario Author Extraction

- **Roadmap stage:** `S2`
- **Plan status:** `CLOSED`
- **Last reconciled:** 2026-09-04

## Purpose

Refactor the canonical monolithic `Main_Agent_Prompt.txt` into a Scenario Author that retains complete semantic analysis and final scenario ownership, materializes one immutable ScenarioGroup per physical unit-test group through the S1 caller contract, and invokes UnitTestGenerator exactly once without owning UnitTestRules projection, RuleCode serialization, schema repair, or Validator orchestration.

## Scope

- Create an S2 implementation slice for all 106 Author rows in the verified Instruction Preservation Matrix.
- Preserve all 48 `SCENARIO_AUTHOR` rows at explicit destinations in the refactored prompt.
- Split all 39 `SHARED_CONTRACT` rows into an exact Scenario Author half and an explicitly deferred Generator/Validator half without duplicate semantic ownership.
- Remove or replace the 18 `UNIT_TEST_GENERATOR` rows and one `VALIDATOR` row from effective Scenario Author behavior while retaining their downstream ownership references.
- Design and add a repository `ScenarioGroup` v1 line-ledger contract with version marker, record grammar, escaping, stable IDs, grouping identity, final semantic evidence, completeness gates, and static examples.
- Refactor `Main_Agent_Prompt.txt` in bounded high-risk batches while treating it as the only canonical Scenario Author prompt artifact.
- Replace `MemoryTemp`, `CreateAIAgentResponseRecord`, direct Validator calls, candidate repair, and CaseID-only response transport with ordered `WriteMemory` ScenarioGroup calls and one UnitTestGenerator handoff defined by the verified S1 contract.
- Fix the Scenario Author external-interface allowlist to exactly `GetCaseData`, `KnowledgeTool`, `RuleCrawler`, `WriteMemory` with Type `ScenarioGroup`, and one `UnitTestGenerator` handoff.
- Preserve RUT/dependency analysis, KnowledgeTool and RuleCrawler discipline, evidence ledgers, assertion and omission decisions, simulation decisions, grouping, confidence/testability, and final semantic audits.
- Preserve the existing bounded two-field external response by mapping Generator `Completed` and `PartiallyCompleted` to external `Completed`, and Generator `Failed` to external `Failed`.
- Create repository-only static fixtures for non-When grouping, homogeneous When grouping, multiple simulation keys, opaque Payload escaping, write failure, and Generator result mapping.

## Excluded Scope

- Modification, parity enforcement, or repurposing of reference-only `Main_Agent.txt` under DEC-017.
- `UnitTestGenerator_Prompt.txt` or `UnitTestGenerator.txt` creation, which belongs to S3.
- `Validator_Prompt.txt` or `JsonValidator_tool.txt` modification, which belongs to S4.
- UnitTestRules JSON construction, RuleCode field mapping, schema selection, schema validation, projection repair, Validator issue handling, candidate writes, or repair-version management inside Scenario Author.
- Changes to either JSON Schema or example family.
- Creation or implementation of Pega `WriteMemory`, `GetMemory`, or `JsonValidationTool`, backing rules, exports, storage, ChangeRequests, or runtime tests under DEC-019.
- End-to-end integration and repository-wide legacy cleanup outside the Scenario Author artifact, which belongs to S5.

## Assumptions and Unknowns

- S0 and S1 are closed and HEAD `b9dd5653f4c449653ac14e06c595e5e2108f516a` is the S2 comparison authority.
- `Main_Agent_Prompt.txt` is the canonical monolith source; its verified baseline SHA-256 is `D6CDED6A4D786AC555452C05296B1A409042B5E6853B0FB9B9EC635AF065C290`, with 177,990 bytes and 2,219 logical lines.
- `Main_Agent.txt` is read-only evidence and is not an S2 deliverable.
- The verified Author matrix contains 106 rows: 48 `SCENARIO_AUTHOR`, 39 `SHARED_CONTRACT`, 18 `UNIT_TEST_GENERATOR`, and one `VALIDATOR` row.
- The verified S1 contract fixes tool signatures, response semantics, exact CaseID/Type/UUID behavior, caller allowlists, failure handling, and Generator/Validator handoffs.
- Exact ScenarioGroup record grammar, escaping, row-check catalog, trace projection, and deterministic complexity derivation are `VERIFIED` by focused independent `PASS`.
- `UNKNOWN` and external — Pega runtime behavior of user-owned tools. S2 may verify only repository prompt and fixture behavior.
- Scenario Author continues to use the existing external identity unless a later explicit decision renames a Pega rule; S2 changes role instructions, not `Main_Agent.txt` or Pega rule metadata.

## Dependencies

- Closed S0 Instruction Preservation Matrix in `docs/execution/plans/S0-baseline-contracts.md`.
- Closed S1 caller contract in `docs/contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md`.
- Accepted DEC-001 through DEC-008, DEC-011, DEC-012, and DEC-016 through DEC-021.
- Canonical source prompt `Main_Agent_Prompt.txt` and read-only Knowledge Area, RuleCrawler, schemas, and examples as semantic evidence.
- Independent read-only subagent availability for the activation plan, design freeze, every high-risk prompt batch, and final S2 review.

## Milestones

1. Validate this S2 activation plan, source baseline, matrix counts, excluded artifacts, batch boundaries, and acceptance criteria through an independent read-only review.
2. Create the S2 implementation slice covering all 106 Author matrix rows; identify exact keep/split/replace/remove destinations and regression evidence.
3. Design the versioned `ScenarioGroup` v1 contract, escaping rules, required records, semantic completion gate, grouping key, and static fixtures.
4. Independently validate the combined row-slice and ScenarioGroup design-freeze package; no prompt edit may begin before a `PASS` verdict and root reconciliation.
5. Refactor the prompt role, authority hierarchy, tool allowlist, execution outline, and external result boundary; remove monolithic candidate/Validator ownership.
6. Independently validate the role/interface batch and reconcile all findings.
7. Refactor the evidence, dependency, RUT execution, assertion, simulation, and omission instructions into Scenario Author-owned semantic phases without weakening stable gates.
8. Independently validate the semantic-preservation batch and reconcile all findings.
9. In one indivisible final S2 batch, implement IPM-AUTH-093–106, replace legacy persistence/serialization with the complete ScenarioGroup grammar, ordered `WriteMemory` calls, UUID collection, and one Generator handoff, and run the complete forward/reverse matrix and forbidden-responsibility audits.
10. Obtain one full independent read-only review of the complete final batch and all S2 acceptance criteria; reconcile findings and require follow-up only when corrections change high-risk behavior.
11. Close S2 only after `PASS`, then create the user-authorized S2 checkpoint commit and push `main` to `origin`; report any Git/remote failure without weakening verification claims.

## Progress

- `VERIFIED` — S0 closed with all 106 Author rows mapped and independently reviewed.
- `VERIFIED` — S1 closed with a repository-only caller contract and F01–F13 fixtures after focused independent `PASS`.
- `VERIFIED` — clean S1 closure commit `b9dd5653f4c449653ac14e06c595e5e2108f516a` is the S2 comparison authority.
- `VERIFIED` — canonical `Main_Agent_Prompt.txt` matches its recorded S0 hash, byte count, and 2,219-line baseline at S2 activation.
- `VERIFIED` — matrix owner counts are 48 Scenario Author, 39 shared, 18 Generator, and one Validator row.
- `VERIFIED` — this S2 activation plan and Roadmap/continuity activation state passed focused independent follow-up after the root corrected all one-high/two-medium first-review findings.
- `VERIFIED` — the fully corrected design-freeze package received focused independent `PASS`; all six prior functional defects and the final DEC-020 reverse-traceability defect are closed.
- `VERIFIED` — prompt batch 1 refactors role, authority hierarchy, closed allowlist, source order, 20-step execution outline, exact ScenarioGroup storage/Generator handoff, and external result mapping; all 26 IPM rows passed independent follow-up.
- `VERIFIED` — prompt batch 2 refactors the complete semantic Knowledge/evidence/dependency/runtime/assertion/simulation/omission/Scenario-freeze layer; all 66 rows passed focused independent follow-up after correction of the checker and fractional score boundary.
- `VERIFIED` — the consolidated final batch implements IPM-AUTH-093–106, complete ScenarioGroup materialization, final handoff, and S2-wide closure checks under DEC-021; the full audit findings were corrected and focused independent follow-up returned `PASS`.
- `VERIFIED` — final root reconciliation reproduced the S2 checker, JSON parsing, prompt hash/encoding, product-file scope, unchanged `Main_Agent.txt`, clean diff checks, and the 106-row census; every mandatory acceptance criterion is satisfied and S2 is closed.
- `VERIFIED` — this closed plan and all authorized S2 artifacts are included in the S2 checkpoint commit pushed from `main` to `origin`; resolve its exact hash from Git because a commit cannot embed its own hash.

## Acceptance Criteria

- The S2 implementation slice accounts for all 106 Author matrix rows and gives every row one explicit S2 action, destination, downstream owner when applicable, regression evidence, and status.
- All 48 Scenario Author rows remain effective, and every Scenario Author-relevant half of the 39 shared rows is implemented without importing Generator or Validator ownership.
- All 18 Generator rows and the one Validator row are absent from effective Scenario Author responsibilities and remain traceable to their future destination.
- `Main_Agent_Prompt.txt` is the only S2 product prompt changed; `Main_Agent.txt`, Generator, Validator, schema, example, Knowledge Area, and external Pega tool artifacts remain unchanged.
- Scenario Author owns only semantic analysis, final scenario formation, grouping, materialization, and one Generator handoff.
- The ScenarioGroup contract is versioned, deterministic, self-contained for Generator consumption, and includes final RUT context, group identity, scenarios, physical inputs/setup, simulations, ASSERT/SIM/OMIT decisions, execution/evidence records, confidence/testability, escaping, and completeness validation.
- The canonical cross-agent trace grammar from DEC-016 is exact: every Data Page `SIM` record retains `sig=<DP_SIG>` and `params=<normalizedParams>`; the complete OMIT catalog includes `inactive_evaluate_all_scalar` and `inactive_return_values_scalar`; delimiter/newline/backslash encoding is lossless; and the ScenarioGroup contract records mandatory downstream Generator and Validator synchronization.
- Non-When groups contain exactly one scenario. Rule-Obj-When groups contain only scenarios with one exact typed `SIMULATION_GROUP_KEY`; equal keys merge, unequal keys never mix, and group order is stable.
- Each final physical group is written once through `WriteMemory(CaseID, ScenarioGroup, Payload)`; returned UUIDs are preserved opaquely and handed to UnitTestGenerator in deterministic group order.
- Any ScenarioGroup write failure is single-attempt and terminal: no retry, no partial Generator handoff, and no deletion or overwrite of earlier immutable records.
- UnitTestGenerator is called exactly once with exact CaseID, immutable RUTType, and ordered ScenarioGroup UUIDs after all writes succeed.
- Scenario Author does not construct UnitTestRules or RuleCode, load UTC schema/example serialization guidance, invoke JsonValidationTool or Validator, read UnitTestCandidate records, repair projections, or manage candidate UUID versions.
- Scenario Author external-interface access is limited exactly to `GetCaseData`, `KnowledgeTool`, `RuleCrawler`, `WriteMemory` with Type `ScenarioGroup`, and one `UnitTestGenerator` handoff. `GetMemory`, `JsonValidationTool`, direct Validator, `MemoryTemp`, `CreateAIAgentResponseRecord`, and `GetAIAgentResponseRecord` are forbidden and absent from its effective workflow.
- Generator `Completed` and `PartiallyCompleted` map to the exact external Completed response; Generator `Failed`, malformed response, or write failure maps to the bounded external Failed response without exposing internal ledgers or Payloads.
- Repository-only fixtures cover standard and When grouping, stable ordering, multiple keys, escaping-sensitive Payloads, exact tool parameters, write failure, malformed Generator response, and all Generator status mappings.
- Every high-risk design or prompt batch and the completed S2 stage receive an independent read-only `PASS` reconciled by the root agent.

## Validation

- Use Git status, `git diff --check`, named-file diffs, and hashes against HEAD `b9dd5653f4c449653ac14e06c595e5e2108f516a` to prove scope and product integrity.
- Parse the Instruction Preservation Matrix and prove the 48 + 39 + 18 + 1 owner partition totals 106 with no missing or duplicate Author row.
- Validate every implementation-slice row against its source range in `Main_Agent_Prompt.txt`, destination text, and relevant DEC/IPM contract.
- Verify the ScenarioGroup grammar and every fixture with a deterministic local parser/checker created in S2; treat parser results as repository contract evidence only.
- Search effective Scenario Author instructions for forbidden candidate JSON, RuleCode serialization, UTC schema selection, JsonValidationTool, direct Validator, GetMemory, candidate repair, and legacy transport responsibilities.
- Search for required semantic responsibilities, exact grouping/cardinality, WriteMemory signature and result handling, ordered UUID handoff, outer status mapping, and all canonical trace records.
- Verify the exact DEC-016 tokens `sig=<DP_SIG>`, `params=<normalizedParams>`, `inactive_evaluate_all_scalar`, and `inactive_return_values_scalar` in the ScenarioGroup grammar and fixtures; test lossless delimiter/newline/backslash encoding and record the S3/S4 synchronization obligation.
- Parse the final Scenario Author external-interface section as a closed allowlist and prove that it contains exactly `GetCaseData`, `KnowledgeTool`, `RuleCrawler`, `WriteMemory`, and `UnitTestGenerator`, with the required Type/call-count restrictions and none of the forbidden interfaces.
- Reproduce the `Main_Agent_Prompt.txt` baseline hash before edits; after each batch, record the intended sections changed and verify unrelated product artifacts against HEAD.
- Verify `Main_Agent.txt` remains byte-identical to HEAD and is never used as a parity target.
- Run static non-When, homogeneous When, unequal-key, order-preservation, escaping, write-failure, and Generator-result fixtures.
- Treat all Pega runtime behavior as external and unverified under DEC-019.
- After each high-risk batch, give the independent reviewer the changed files, baseline prompt, exact implementation-slice rows, decisions, S1 contract, fixtures, commands, and acceptance criteria.
- At S2 closure, run a reverse audit from every effective prompt instruction to one source matrix row or accepted decision and verify no conflicting duplicate or orphaned stable behavior remains.

## Evidence

- `VERIFIED` — HEAD `b9dd5653f4c449653ac14e06c595e5e2108f516a` contains the independently verified S1 contract and clean S1 closure state.
- `VERIFIED` — `Main_Agent_Prompt.txt` matches recorded hash `D6CDED6A4D786AC555452C05296B1A409042B5E6853B0FB9B9EC635AF065C290`, 177,990 bytes, and 2,219 logical lines.
- `VERIFIED` — the S0 matrix contains exactly 106 Author rows partitioned into 48 Scenario Author, 39 shared, 18 Generator, and one Validator owner.
- `VERIFIED` — DEC-017 excludes `Main_Agent.txt`; DEC-019 excludes external Pega tool implementation and runtime proof.
- `VERIFIED` — S2 activation planning passed focused independent follow-up after the root corrected the first review's DEC-016, S5 scope, and closed-allowlist findings; the reviewer reproduced matrix counts, exact-next synchronization, and product integrity with no remaining findings.
- `IMPLEMENTED_NOT_VERIFIED` — `docs/execution/design/S2-instruction-implementation-slice.md`, `docs/contracts/SCENARIO_GROUP_V1.md`, `scripts/validate_s2_design.py`, and five `fixtures/s2/` files form the design-freeze package; the first independent review returned `FAIL` with five high and three medium contract/checker findings, so its earlier root-check PASS is insufficient for prompt work.
- `FAILED` — the second focused review confirmed the first correction batch's envelope, grouping-key, cell/trace, Decision Table, structured-fact, and non-null fixes, but found four high and two medium residual defects: non-executable row-check labels plus literal `NaN`, invalid cross-group signature equality, non-whitelisted SIM trace projection, incomplete COMPLEXITY derivation, missing `C` ID prefix prose, and DTC omitted from `dtCount` prose.
- `IMPLEMENTED_NOT_VERIFIED` — the second root-correction batch replaces the placeholder with 106 exact executable row checks; limits DecisionColumnSignature equality to one physical group; defines exact trace whitelists and positive/negative SIM projection checks; adds DEC-020 with deterministic loop/invocation, tier, and cap derivation plus six boundary cases; and corrects `C` COLUMN and DTC prose. Expanded checker, JSON parsing, exact-next, product-scope/hash, whitespace, and link checks pass locally; focused independent follow-up is pending.
- `FAILED` — the third focused review passed all six prior functional corrections and supporting checks but found one new medium defect: DEC-020 is absent from IPM-AUTH-041 and S2-R041 traceability.
- `IMPLEMENTED_NOT_VERIFIED` — IPM-AUTH-041 and S2-R041 now cite DEC-020, every executable row-check audit carries its exact decision set, and the checker has a specific DEC-020 linkage assertion. Expanded local checker, diff, exact-next, and product-scope checks pass; focused follow-up is pending.
- `VERIFIED` — final focused follow-up returned `PASS` with no findings, independently reproduced the checker, and mutation-tested removal of DEC-020 from either IPM-AUTH-041 or S2-R041. Product files remained unchanged through design freeze.
- `IMPLEMENTED_NOT_VERIFIED` — prompt batch 1 changes only `Main_Agent_Prompt.txt` among product text files; its SHA-256 is `51126AB5836E4D7DB9D0C54E5C729E9F59D25AC25B871E5982022F692868B133`, with 166,207 bytes and 2,068 CRLF logical lines. Expanded checks pass 26 trace markers, exact caller contracts, closed five-interface allowlist, execution order, downstream scope locks, and all prior design fixtures.
- `FAILED` — the first independent prompt-batch review passed behavior but found two medium coherence defects: four stale planning/continuity statements and a false claim that the complete ScenarioGroup grammar was already embedded.
- `IMPLEMENTED_NOT_VERIFIED` — both findings are corrected: all state text reflects prompt batch 1, and the prompt/checker explicitly defer full grammar insertion to the later materialization batch, mark the intermediate prompt non-release-ready, and prohibit WriteMemory/Generator execution until then. Root checks pass at SHA-256 `4A052FD0F5159728F37A9D18BE610776237E9E7D2792222213FE202C60554326`, 166,730 bytes, and 2,068 CRLF lines.
- `VERIFIED` — focused follow-up returned `PASS`, confirmed the two coherence fixes and all regression smoke checks, and found no remaining batch-1 defects. IPM-AUTH-001–020 and 027–032 are verified.
- `IMPLEMENTED_NOT_VERIFIED` — prompt batch 2 adds semantic-only Knowledge acquisition, section-level traces for IPM-AUTH-021–026 and 033–092, internal `SCENARIO_SNAPSHOT`, semantic physical grouping, exact final decision records, omission reasons, and confidence/testability gates. Expanded checks pass 92 unique prompt markers and slice status 26 verified/66 implemented/14 not started. `Main_Agent_Prompt.txt` is SHA-256 `8972DF766EF2837DE7DBEBE859A172D749C5B75EE45D48F7ABCAC1756A69AF06`, 157,467 bytes, and 1,920 CRLF lines.
- `FAILED` — the first independent semantic-batch review found two high and two medium defects: B/A remained candidate-bound and unreachable under the scope lock; DEC-020 formulas/caps were not embedded; ROOT depended on forbidden RuleCode; and the checker did not catch these defects. All other reviewed semantic behavior passed.
- `IMPLEMENTED_NOT_VERIFIED` — all four findings are corrected: executable semantic I/W/F→decisions/group/materialization→B/A→WriteMemory order; candidate-free internal snapshot and B/A definitions; complete embedded DEC-020 derivation; RuleCode-independent ROOT; and 14 mutation-checked critical obligations. Root checks pass at SHA-256 `D3356E2D8A26E1AF7FB98AAA4641255263FC7D867E6B6AA8C7581ED1217F1BD3`, 159,680 bytes, and 1,929 CRLF lines.
- `FAILED` — focused follow-up passed all prompt corrections but found one medium checker false negative: full hard triggers, tier derivation, ROOT freeze/named-page restrictions, weighted formula, and complete RuleCode-independence are not all mutation-protected.
- `IMPLEMENTED_NOT_VERIFIED` — the checker now requires each critical clause exactly once in its required section and mutation-tests all 16 complete workflow, DEC-020, and ROOT-lock clauses. This covers all eight hard-trigger thresholds, the weighted formula, complete tier and cap derivation, limit behavior, full ROOT freeze/named-page restrictions, downstream-only projection, and every RuleCode-independent ROOT source prohibition. The repository-static checker and `git diff --check` pass locally; focused independent review is pending.
- `FAILED` — the first focused checker audit reproduced two medium defects: two workflow clauses could be relocated outside their required sections, and the ELEVATED wording `25–49` was not exact for fractional weighted scores even though executable derivation used the half-open interval below 50.
- `IMPLEMENTED_NOT_VERIFIED` — all three workflow clauses are now section-bound; the checker mutation-tests removal and relocation of all 16 complete clauses; the prompt states exact ELEVATED bounds as `25 <= score < 50`; and fixture cases at 49.75 and 50 close the fractional/high threshold. Root checks pass with `Main_Agent_Prompt.txt` SHA-256 `B88678FE2776D494288CB06BD86D2840107313DCBAB9A1825998E6EA79F62E75`, 159,680 bytes, and 1,929 CRLF logical lines; focused independent follow-up is pending.
- `VERIFIED` — focused independent follow-up returned `PASS` with no findings after 96 adversarial probes covering all 16 removals, relocations, and duplicates plus 48 DEC-020/ROOT fragment mutations. Prompt batch 2 and IPM-AUTH-021–026/033–092 are verified; no Pega runtime behavior was inferred.
- `VERIFIED` — the user accepted DEC-021 risk-based batching and authorized a mandatory commit and push after the final S2 batch passes independent review.
- `IMPLEMENTED_NOT_VERIFIED` — the final batch removes the legacy candidate storage/Validator/serialization tail and adds six Scenario Author pre-materialization gates, the complete executable ScenarioGroup v1 contract, exact ordered storage/handoff, a closed Author prohibition, and downstream-only Generator/Validator preservation. The expanded checker passes all 106 prompt traces, exact embedded/repository contract synchronization, 92 verified plus 14 implemented matrix rows, stale-tail rejection, all prior semantic mutations/fixtures, and product-scope checks. `Main_Agent_Prompt.txt` is SHA-256 `C67208C40275AEFB7438B0CF94969A3F91AE8CACE626A98D29DBB2ADABBFCBD6`, 173,884 bytes, and 1,973 CRLF logical lines.
- `FAILED` — the full independent final audit found three high defects: row checks did not execute against prompt semantics, NotTestable was unrepresentable, and several semantic references could dangle. It also found two medium groups: valid zero-PARAM/simulation-state/DTA-OMIT alternatives were rejected or untested, and Roadmap/continuity/slice classifications were stale.
- `VERIFIED` — corrections add full-prompt SHA-256/CRLF regression for all 106 traced rows; complete RX/BRANCH/PRODUCER/PROPERTY reference checks and negative mutations; zero-PARAM, NotTestable, schema-aligned SupportLevel, RequiredButLimited, NotApplicable, and DTA-OMIT behavior with a new fixture; and reconciled operational state. Focused independent follow-up returned `PASS` with no high- or medium-severity findings and independently mutation-tested the corrected behaviors.
- `VERIFIED` — the final S2 prompt is 174,283 bytes and 1,973 CRLF logical lines with no BOM and SHA-256 `BACADFB07E90D68B9751B9D573437A21B204E0BCCE87BE6ACE8BD5DDF3CEEC95`; all 106 rows, five ledgers, six scenarios, orchestration fixtures, alternative states, 12 ledger mutations, 16 semantic mutations, and 16 relocation probes pass repository-static validation. Pega runtime remains external and unverified.
- `VERIFIED` — final root reconciliation on 2026-09-04 confirmed all S2 acceptance criteria, no generated cache artifacts, no unintended product-file changes, valid JSON fixtures, and a clean `git diff --check`; the independently reviewed S2 state is closed.

## Risks

- The 2,219-line monolith interleaves semantic and projection responsibilities. Broad deletion can orphan stable gates; every prompt batch is high-risk and must stop for independent review.
- Shared matrix rows can accidentally duplicate ownership across Scenario Author and Generator. The row-level slice must state the exact Author half and deferred half before prompt edits.
- Candidate-oriented final gates contain semantic checks that must move into ScenarioGroup finalization rather than being deleted with RuleCode serialization.
- A ScenarioGroup grammar that omits runtime execution, producer, simulation, Decision Table, or assertion-decision evidence would force Generator to repeat semantic analysis and violate DEC-001/005/006.
- Incorrect escaping can corrupt opaque Payloads even when Memory is correct. Grammar fixtures and a deterministic parser/checker are required before prompt integration.
- Removing MemoryTemp can leave competing implicit ledgers or stale scenario state. One complete replacement snapshot must remain the sole final scenario authority before materialization.
- A partial write followed by Generator invocation would violate complete ordered handoff. Write failure must be terminal with no Generator call.
- Status mapping can leak partial-failure details or incorrectly expose `PartiallyCompleted` as failure. Static result fixtures must lock the two-field external response.
- Reference-only `Main_Agent.txt` can be accidentally edited or used as a parity target. Hash and scope checks must run after every batch.
- Repository fixtures cannot verify user-owned Pega runtime behavior; no S2 claim may promote static evidence to runtime verification.

## Exact Next Action

Create and independently validate the S3 ExecPlan before activating S3 or changing `UnitTestGenerator` product artifacts.

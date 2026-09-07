# ExecPlan: S3 Unit Test Generator

- **Roadmap stage:** `S3`
- **Plan status:** `ACTIVE` — activation and checker prerequisite independently verified; design freeze is next.
- **Last reconciled:** 2026-09-07

## Purpose

Add the sequential Pega agent `UnitTestGenerator`. It consumes the ordered, immutable ScenarioGroup UUIDs from Scenario Author, projects one combined schema-governed UnitTestRules candidate, delegates validation using the current candidate UUID, and performs at most two projection-only repair attempts. It returns runtime success and untestable-scenario details without taking ownership of semantic analysis.

## Scope

- Create `UnitTestGenerator_Prompt.txt` as the canonical prompt and `UnitTestGenerator.txt` as its Pega agent export (DEC-013/014).
- First repair the existing S2 checker's checkout-line-ending dependency without changing the independently reviewed Scenario Author prompt or its logical contents. Verify both LF and CRLF representations against one fixed canonical digest; reject content mutations, BOMs, lone CRs, and invalid encodings. Retain historical raw-hash evidence.
- Create `docs/execution/design/S3-instruction-implementation-slice.md`, accounting for all 106 Author matrix rows and all 44 Validator rows. Implement the 18 Generator-owned rows and the Generator half of every applicable shared row; explicitly mark Author-only and S4-only obligations as excluded or deferred with their owners.
- Create `docs/contracts/UNIT_TEST_GENERATOR_V1.md` defining input validation, ordered exact reads, the closed interface allowlist, structural Knowledge acquisition, ScenarioGroup parsing and immutable-source checks, projection, rejection scope, repair budget, and the complete `GeneratorRunReport`.
- Add deterministic repository-static fixtures and a checker under `fixtures/s3/` and `scripts/`, covering both candidate schema families, source-to-candidate correspondence, call traces, rejection/pruning, UUID versions, bounded repairs, and reports.
- Define the Generator-facing Validator route/issue consumer contract sufficiently for static S3 tests. Record every required S4 producer change; S3 does not claim the current legacy Validator implements the future contract.
- Select and record non-contractual Pega agent metadata from inspected repository evidence, and synchronize the prompt and explicit caller interface configuration into the new export. Distinguish repository artifact validity from Pega import/runtime proof.

## Excluded Scope

- Semantic RUT/dependency analysis, RuleCrawler/GetCaseData calls, new expected values, coverage, assertions, simulations, grouping decisions, or reinterpretation of DEC-020 complexity caps.
- Changes to `Main_Agent_Prompt.txt`, reference-only `Main_Agent.txt`, `Validator_Prompt.txt`, `JsonValidator_tool.txt`, either schema/example family, Knowledge Areas, or the RuleCrawler export. A discovered blocking handoff defect requires a separately reviewed correction and synchronized decisions/contracts before dependent Generator work.
- Pega tool/backing-rule implementation, Memory storage design, Rule-AI-Tool exports, ChangeRequests, live Pega mutation, or runtime verification under DEC-019.
- S4 Validator implementation and S5 whole-flow integration/legacy cleanup.
- Further commits or any push without additional explicit user authorization. The user authorized the current local preparation checkpoint on 2026-09-07 under GitHub `vkoloskov`; it includes the DEC-023/024 documentation changes and preserves pre-existing `.idea/` outside Git.

## Assumptions and Unknowns

- S0, S1, and S2 are historically closed. At S3 activation, HEAD and local `origin/main` were `4161fd3f77fc562ecb1e9fded19b5391ea67722f`; the S2 checkpoint is `36f097a842296b0e9b4de30cbb1ce27046c5ff0c`. The current local preparation checkpoint follows `4161fd3` and has not been pushed; resolve its exact hash from Git and current operational state from continuity.
- The original canonical monolith is recoverable from Git commit `b9dd5653f4c449653ac14e06c595e5e2108f516a:Main_Agent_Prompt.txt`. Matrix source line ranges refer to that pre-S2 version, not to current line numbers. Retrieve it read-only for clause-level preservation work; never use `Main_Agent.txt` for parity.
- Current `Main_Agent_Prompt.txt` is byte-identical to HEAD: 172,310 bytes, 1,973 LF endings, zero CRLF endings, SHA-256 `6F059B641B9CF8B627E6879ED5B7A8FAEE78A616E71E2DD305AF8C051ACD215F`. Converting LF to CRLF in memory reproduces the historical S2 hash `BACADFB07E90D68B9751B9D573437A21B204E0BCCE87BE6ACE8BD5DDF3CEEC95`.
- At activation, the unmodified S2 checker failed on that representation difference. The DEC-025 correction now passes full local and independent checks; the first review's documentation-only findings are corrected and focused follow-up returned `PASS`. This does not change S2 semantic content or rewrite its historical raw-hash evidence.
- S1 fixes tool envelopes and transport behavior, ScenarioGroup v1 fixes the source grammar, and S0 fixes instruction ownership. Generator must consume these contracts rather than weaken them to fit implementation.
- The full report shape, precise index/remapping rules, malformed-source rejection boundaries, Pega metadata, and static projection test cases must be resolved and independently reviewed during design freeze. Do not present these implementation choices as previously accepted decisions.
- `UNKNOWN` — sufficiency of formal RUT parameter-type evidence for projection. Original monolith lines 1554–1565 require the formal Pega parameter type and forbid inferring it from the value; ScenarioGroup PARAM exposes valueType without a dedicated formal-type field. Design must verify whether existing INPUT mode/evidence conveys the required distinction (including String, Integer, Decimal, Boolean, and PAGE); if insufficient, use the separately reviewed handoff-correction path rather than guess the type.
- Current Validator uses the legacy interface. S3 may validate the future consumer using static reports; executable three-agent compatibility belongs to S4/S5.
- Pega import and runtime remain `UNKNOWN` and external. Availability of a full Draft 2020-12 package must be probed before schema checks; if absent, use the accepted two-implementation assertion-keyword fallback and report its exact limits.

## Dependencies

- [Roadmap](../ROADMAP.md), [continuity gate and reviewer profiles](../CONTINUITY.md), and [decisions](../../decisions/DECISIONS.md), especially DEC-001–014 and DEC-016–024.
- [S0 matrix](S0-baseline-contracts.md), [closed S2 plan](S2-scenario-author-extraction.md), and [verified S2 instruction slice](../design/S2-instruction-implementation-slice.md).
- [S1 caller contracts](../../contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md), including F01–F13, and [ScenarioGroup v1](../../contracts/SCENARIO_GROUP_V1.md).
- Both immutable-RUTType-selected schema/example families and original monolith projection clauses.
- Independent read-only reviewers using explicit `gpt-6-astra` / `xhigh` for activation, design freeze, each indivisible high-risk batch, and stage closure. No silent profile substitution.

## Milestones

1. Independently validate this activation plan and reconcile it against Git, S0/S1/S2 contracts, stage dependencies, preservation scope, and the known checker failure. Activate S3 only after `PASS` and root reconciliation.
2. Repair and independently validate the S2 checker prerequisite. Require the complete S2 checker to pass for the present LF checkout and equivalent CRLF input, and prove content/encoding corruption still fails. Do not convert product files.
3. Build one coherent S3 design-freeze package: complete matrix slice; Generator contract and report schema; exact structural Knowledge keys; source-ledger projection mapping; rejection/index/remapping rules; candidate/version orchestration; Pega agent metadata/interface design; positive and negative static fixtures and executable checks.
4. Independently validate that package against every relevant source clause and acceptance criterion. Stop before product prompt/export creation until `PASS` and root reconciliation. Add explicit decisions for any new durable interpretation of underspecified source behavior.
5. Implement the complete Generator prompt and export as one cohesive high-risk batch from the frozen design. Add prompt/export parity and interface-configuration checks; exercise both schema families and the complete source/projection/repair/report suite. Use the original monolith and immutable source fixtures to detect lost rules, not merely prompt labels or self-repeating assertions.
6. Obtain independent whole-stage review of the completed batch and every S3 acceptance criterion. Root applies corrections; high-risk corrections require focused follow-up. Untouched verified sources are rechecked by Git/hash and cross-cutting invariants rather than repeated clause-by-clause audits.
7. Close S3 only after all mandatory checks and independent `PASS` are reconciled. Update continuity and Roadmap to the S3/S4 boundary with one next action. Do not activate S4 or imply runtime compatibility from S3 static evidence.

## Progress

- `VERIFIED` — the current preparation checkpoint is committed locally under the user-authorized `vkoloskov <95134563+vkoloskov@users.noreply.github.com>` author/committer identity. It includes six project paths and the checkpoint reconciliation, excludes `.idea/`, and is not pushed. Resolve the self-referential commit hash from Git; S3 milestones and next action are unchanged.

- `VERIFIED` — restart read the continuity artifacts, closed S2 plan, relevant decisions, and root AGENTS.md; Git status/log confirm the recorded four modified documentation files, `main`/local `origin/main`, and pre-existing `.idea/`.
- `VERIFIED` — no Generator artifact or S3 plan existed at restart; S3 was `NOT_STARTED`.
- `VERIFIED` — independent read-only `/root/review_s3_activation` used `gpt-6-astra` / `xhigh`, returned `PASS` with no findings, and independently reproduced Git, source/matrix counts, prompt hashes, links, next action, whitespace, and the known S2 failure. Root reconciled the report and activated S3 on 2026-09-07.
- `VERIFIED` — DEC-025 checker correction accepts uniform LF/CRLF using the fixed canonical digest, retains historical equivalence, and rejects eight content/encoding mutations. Full S2 validation passes locally and independently; `/root/review_s2_portability` returned focused `PASS` after root documentation reconciliation, with no functional corrections required.
- `NOT_STARTED` — S3 design freeze, Generator prompt/export, static S3 suite, and stage closure.

## Acceptance Criteria

1. Activation plan and prerequisite checker correction receive independent `PASS`. The unchanged Scenario Author passes current S2 regression, including positive LF/CRLF equivalence and negative content/encoding cases, with no weakened semantic checks.
2. Every one of the 150 S0 matrix rows is dispositioned in the S3 slice. All 18 Generator and every applicable shared obligation have exact original-source clauses, one effective Generator destination, decisions, executable regression evidence, and truthful status. Author/Validator halves retain their distinct owners.
3. `UnitTestGenerator(CaseID, RUTType, ScenarioGroupUUIDs)` consumes exact CaseID, immutable original RUTType, and the supplied nonempty ordered opaque UUID array. Exact `GetMemory` reads occur once per supplied UUID in order. A failed/malformed read terminates the run; no fallback, retry, or silently missing group is allowed.
4. Generator's closed interface allowlist is exactly `KnowledgeTool` for structural UTC/schema/example guidance, `GetMemory` for `ScenarioGroup`, `WriteMemory` for `UnitTestCandidate`, and `UnitTestValidator` with the current candidate UUID. No semantic acquisition, direct JsonValidationTool, candidate reads, legacy transport, or separate result writes.
5. Source grammar/version, CaseID/RUTType/group identity, cardinality, typed simulation keys, complete ledger records, references, escaping, and immutable semantic decisions are checked before projection. Invalid inputs have explicit deterministic rejection scope; unavailable ordered input is always terminal under S1.
6. One combined `{ "UnitTestRules": [...] }` candidate preserves group order and contains one entry per surviving supplied physical group. Non-When entries have one scenario; surviving When scenarios retain order and shared simulation configuration. Generator never merges/splits groups, invents coverage, or silently changes a semantic cell. Pruning removes only an identified rejected scenario or the complete affected group and remaps projection indices without changing stored IDs or ledgers.
7. Projection preserves all source-driven metadata, parameters, setup/page/class/root context, typed values, comparator rules, page/list/Param assertion shape, DP simulation identity/payload, exact RuleCode-to-trace bijection, and EvidenceSummary/Reasoning facts. DEC-016 SIM `sig=<DP_SIG>` and `params=<normalizedParams>` and both `inactive_evaluate_all_scalar` and `inactive_return_values_scalar` omission reasons remain exact. DEC-020 metrics/tier/caps are copied without reinterpretation.
8. Schema and structural Knowledge selection derives only from immutable original RUTType, using exact existing schema/example filenames and KnowledgeTool composite keys. Guidance is cached once before validation. Repairs make no new Knowledge or semantic calls.
9. Candidate writes use the exact S1 envelope. Initial projection and every permitted repaired/pruned projection create new immutable candidate UUIDs. Only the successful current UUID reaches Validator. Any write failure is terminal, single-attempt, and cannot fall back to an older candidate.
10. Generator consumes `OK`, `GENERATOR_REPAIR`, `SEMANTIC_REJECT`, and `HUMAN` with `HUMAN > SEMANTIC_REJECT > GENERATOR_REPAIR > OK` precedence; validates the report structure, counts, route/action consistency and coordinates; treats malformed, contradictory, unscopable, or candidate-wide fatal reports as terminal. Warning-only valid `OK` remains successful. Standard scenario-local, When scenario-local, shared-group, mixed-scope, and candidate-wide cases are tested against the current candidate's index map.
11. Repairs affect JSON shape, fields, naming, indices, or alignment to existing ASSERT/SIM/OMIT only. Mass-error rebuild uses unchanged sources. Maximum validation is the initial report plus two repair attempts, with one shared budget for every candidate revision, including pruning. No semantics, source Memory, expected values, or original RUTType changes. All-failed and budget-exhausted behavior is explicit and tested.
12. The complete `GeneratorRunReport` is one bounded raw JSON runtime report with `Completed`, `PartiallyCompleted`, or `Failed`, exact successful-candidate reference when applicable, and stable source-addressed success/untestable details. Success requires current-candidate Validator `OK`; partial status requires both retained validated output and rejected scenarios. Failure cannot expose an earlier candidate as successful. Author's existing status mapping remains compatible; no report record is persisted.
13. The new Pega rule is named `UnitTestGenerator`, has the exact input/output and closed interface configuration, and contains exactly one `pySystemPrompt` pair semantically equivalent to its canonical prompt after documented decoding. Chosen metadata has repository evidence; no unrelated legacy export, schema, example, or Knowledge file changes.
14. Static positive and adversarial fixtures exercise both schema families, one/multiple When simulation groups including no simulation, opaque escaping and UUIDs, order, typed values, trace/cell bijection, empty inputs, Param/page/list assertions, omissions, NotTestable and partial success, scenario/group/candidate rejection, malformed responses, wrong UUIDs, repair freshness and exhaustion, and the outer status mapping. Candidate examples pass the selected schema validation method with its limits recorded.
15. Every required independent review uses the prescribed actual model/effort and returns `PASS`; root reconciles evidence. No S3 closure claim depends on unverified Pega tool internals, live import, or future S4 implementation.

## Validation

- Run `git status --short --branch`, `git diff --check`, targeted diffs, and product hashes against current HEAD. Preserve `.idea/` and the pre-existing documentation updates. Verify all relative documentation links and exactly one synchronized next action in this plan and continuity.
- Reproduce the recorded failure with `python3 -B scripts/validate_s2_design.py` before changing the checker. After the correction, rerun the full checker and positive/negative line-ending tests, including a semantically changed prompt with otherwise valid formatting. Verify product bytes still match HEAD.
- Read original source via `git show b9dd5653f4c449653ac14e06c595e5e2108f516a:Main_Agent_Prompt.txt`; verify source line ranges and matrix counts by parsing the S0 table. Check all 150 S3 dispositions and reverse-audit every effective Generator instruction to its source row or accepted decision.
- At design freeze, define concrete checker commands and executable fixture expectations in the slice and this plan. Fixtures must fail when group order, source values, SIM signatures/parameters, trace cells, UUID freshness, repair budget, or report scope are mutated. Labels alone do not establish executable preservation evidence.
- Parse JSON with UTF-8 BOM support and reject duplicate keys/non-finite values in generated candidates. Probe for a complete Draft 2020-12 validator; otherwise apply the accepted independently checked two-implementation fallback to every assertion keyword the schemas use. Distinguish static schema conformance from external Pega validation.
- Decode the new export's bounded `pySystemPrompt` content using the observed serialization format; compare logical prompt lines/tokens, count boundaries, and audit explicit inputs/tools/metadata. Validate targeted export structure without using reference-only `Main_Agent.txt` for parity or modification.
- Require the completed static S3 checker plus current S2 regression, named-artifact integrity, relative links, whitespace, cache hygiene, and final independent acceptance audit before S3 closure.

## Evidence

- `VERIFIED` — focused prerequisite follow-up `/root/review_s2_portability` used `gpt-6-astra` / `xhigh` and returned `PASS` with no remaining findings. Root confirmed both requested documentation corrections, unchanged functional diff/product scope, synchronized next action, local links, and whitespace. Milestones 1 and 2 are complete; milestone 3 design freeze is next.

- `FAILED` — first prerequisite review `/root/review_s2_portability` used `gpt-6-astra` / `xhigh` and returned `FAIL` solely for two stale current-state statements in this plan. Independent functional checks passed: complete LF/CRLF runs, 26 rejected adversarial mutations, fixed digests, unchanged pre-existing checker functions except intended integration, unchanged 15 product files/contracts, and continued ScenarioGroup CRLF rejection. Root corrected the two statements as historical observations; focused follow-up returned `PASS` with no remaining findings. This entry retains the first-review verdict as historical evidence.

- `VERIFIED` — the corrected `python3 -B scripts/validate_s2_design.py` passes all five ledgers/six scenarios, 106 executable row checks, existing semantic/ledger/orchestration probes, and eight new integrity mutations. Isolated temporary-checkout runs pass for complete LF and CRLF prompts and fail for changed semantic content under CRLF. All tracked product `.txt` files remain byte-identical to HEAD; no cache artifacts exist; `git diff --check` passes. Independent prerequisite review and root reconciliation are complete.

- `VERIFIED` — `git log -5 --oneline --decorate` on 2026-09-07 shows HEAD/local `origin/main` at `4161fd3`, parent S2 checkpoint `36f097a`, S1 source checkpoint `b9dd565`, and S0 baseline `99e0383`.
- `VERIFIED` — pre-correction root inspection and execution confirmed the HEAD checker pinned the CRLF raw digest and required exactly 1,973 CRLF endings, reproducing the LF failure. The corrected checker now accepts the equivalent uniform LF/CRLF representations and passes the recorded full-suite runs.
- `VERIFIED` — S1 sections 3, 6, 7, 9, and 10 fix the role allowlists, terminal read/write failures, ordered group reads, initial report plus two repair attempts, immutable candidate versions, and runtime-only partial status. S3 fills the report shape left open by S1 section 9.3.
- `VERIFIED` — activation review `/root/review_s3_activation` returned `PASS` on 2026-09-07 with actual `gpt-6-astra` / `xhigh`; root verified unchanged product/checker bytes, 150 source rows, 20 local links, synchronized next action, and clean whitespace before activation.
- `VERIFIED` — fresh `python3 -B scripts/validate_s2_design.py` reproduced the recorded full-regression SHA-256 failure before correction; Python3 has no installed `jsonschema` package.

## Risks

- Activation changes the operational stage and must stop at milestone 1's independent read-only gate before S3 activation.
- Weakening the S2 hash guard could hide lost stable instructions. Milestone 2 requires positive LF/CRLF and negative content/encoding probes plus independent read-only review before design relies on the restored checker.
- Design freeze changes agent interfaces, rejection/repair policy, grouping interpretation, and trace projections. Treat milestone 3 as one high-risk package and stop at milestone 4's independent read-only gate before product implementation.
- Incomplete ledger projection can force hidden semantic reconstruction; the source-to-field map, immutable-input fixtures, and original-clause review must expose gaps before coding the prompt.
- Pruning changes candidate positions; stale issue indices or UUIDs can target the wrong scenario/version. Maintain a current-candidate source map and test remapping through repeated mixed failures within the fixed budget.
- The Generator prompt and new export are one high-risk batch at milestone 5. Stop for milestone 6's independent whole-stage audit; root applies all changes and obtains focused follow-up when a blocking correction alters behavior.
- Export metadata can look syntactically credible without a usable Pega import. Record observed provenance and repository checks; retain external runtime/import uncertainty rather than fabricate success.
- Existing Validator artifacts are incompatible until S4; static consumer reports must not be confused with end-to-end integration evidence.

## Exact Next Action

Build and independently validate the S3 design-freeze package, resolving formal parameter-type provenance before Generator prompt/export implementation.

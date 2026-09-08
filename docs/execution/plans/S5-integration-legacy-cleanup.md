# ExecPlan: S5 Integration and Legacy Cleanup

- **Roadmap stage:** S5
- **Plan status:** CLOSED — independent whole-stage PASS and root reconciliation complete; all13criteria VERIFIED.
- **Last reconciled:** 2026-09-08

## Purpose

Complete the repository refactor by proving the Scenario Author -> UnitTestGenerator -> UnitTestValidator caller flow, preserving all stable source obligations and removing obsolete transport names from effective deliverables. Finish S5 with independent whole-stage PASS and root reconciliation. This is repository-static integration, not live Pega execution.

## Scope

- Effective deliverables are Main_Agent_Prompt.txt, UnitTestGenerator_Prompt.txt, UnitTestGenerator.txt, Validator_Prompt.txt and JsonValidator_tool.txt. Main_Agent.txt remains reference-only and byte-identical to the activation baseline.
- Inspect and prepare a bounded cleanup of residual legacy transport references in Main/Generator prompts, including prohibitions and overridden historical clauses. Preserve the semantic gates and explicit downstream-only ownership locks; do not merely delete obligations or make obsolete candidate work executable in Author.
- Resolve demonstrated caller-contract mismatches before integration: Author currently rejects extra Memory metadata allowed by S1; shared embedded SIM prose must express the accepted DEC-030 candidate-only evidence boundary consistently. Freeze exact source/replacement text and evidence in a reviewed S5 design before product changes.
- Create a reverse 150-row matrix linking every original obligation to one accountable authority and distinct executing responsibilities. Shared invariants have an authoritative source/owner and separately stated producer/projection/validation checks, not duplicate semantic derivation. Account explicitly for accepted transport removal and non-executable historical text.
- Add a static Author storage/handoff adapter starting with final audited ScenarioGroup payload fixtures, connected to the existing real source parser, Generator protocol/projector, Validator producer and full Draft 2020-12 candidate/report schemas. Use local in-memory external-tool test doubles; do not implement Pega tools.
- Cover standard and When success, partial success, multiple When groups, Scenario/group/candidate rejection, all-failed, wrong-address/UUID, repair-version and shared two-repair-budget flows. Use actual Validator-produced reports for validation paths; label every deliberate candidate/transport fault, separate source and candidate memory, audit unmodified projections against immutable source and check every final surviving candidate.
- Verify exact opaque addressing, one write attempt, schema-first short circuits, immutable history, current-coordinate pruning/remapping, closed per-agent tool allowlists and Author's existing two-field status mapping with bounded failures.
- Create deterministic current artifact reconstruction, exact decoded pair parity, protected metadata/hashes and mutation tests. Preserve all baseline artifacts except the explicit approved Main/Generator product deltas. Keep historical S2/S3/S4 code, contracts, fixtures and manifests unchanged; run their full gate against an isolated local checkout of fixed S4 baseline, then separately prove current products differ only by reviewed deltas and current integration tests exercise unchanged runtime implementations.

## Excluded Scope

- Main_Agent.txt edits/parity; new Author export; external tools/backing rules/categories; Pega environment calls, import, deployment or runtime; target Ruleset/Version selection, already implemented in Pega.
- New semantic acquisition, source revision, schema/report/catalog change, new RUT behavior, storage protocol, parallel orchestration or weakened repair/source gates.
- Push and other remote mutations. The initial S5 request excluded commits; the subsequent 2026-09-08 request authorizes the local S5 closure checkpoint under the same vkoloskov identity.
- Rewriting all historical prompt prose or removing already verified source evidence indiscriminately. Any newly found behavioral defect requires a bounded evidenced correction and independent high-risk review before dependent work.

## Assumptions and Unknowns

- Verified activation HEAD is d4061046650c87b9da2c4f87141f23aa2602f082; parent4393c680633d176129676f7b91179262cc25391f. main is three commits ahead of unchanged local origin/main4161fd3f77fc562ecb1e9fded19b5391ea67722f. Only pre-existing .idea/ is untracked.
- S0–S4 are CLOSED. S4 whole-stage PASS covered all14criteria,35producer groups,57protectedartifacts,150rows/73effective,10reports and sevenS3suites/180corrections. Existing runtime Python modules are repository-static oracles, not deployed agents.
- Author semantic analysis is represented by pre-audited source fixtures and existing source checks. A static adapter must not claim to simulate arbitrary RUT reasoning, an LLM or free-text UTC interpretation.
- DEC-030 limits absent signature/parameter/binding proof to Generator's source audit; every observable candidate comparison remains required. S5 must not fabricate missing candidate carriers.
- A local temporary checkout may be used only for fixed historical regressions; its mutations do not affect the user's index/checkout. Current artifact checks and integration cannot be replaced by a historical PASS.
- User-owned Pega implementations and import/reference resolution remain UNKNOWN and are not repository closure blockers.

## Dependencies

- [Continuity](../CONTINUITY.md), [Roadmap](../ROADMAP.md), [Decisions](../../decisions/DECISIONS.md), especially DEC-001–008/011–012/016–019/023–024/028–030.
- [S0 matrix](S0-baseline-contracts.md), [S2 slice](../design/S2-instruction-implementation-slice.md), [S3 slice](../design/S3-instruction-implementation-slice.md), [S4 slice](../design/S4-instruction-implementation-slice.md).
- [S1 caller contract](../../contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md), [ScenarioGroup 1.3](../../contracts/SCENARIO_GROUP_V1.md), [Generator](../../contracts/UNIT_TEST_GENERATOR_V1.md), [Validator](../../contracts/UNIT_TEST_VALIDATOR_V1.md), [S4 acceptance](../design/S4-acceptance-report.md).

## Milestones

1. Obtain independent activation-plan PASS and root reconciliation, then activate S5 without changing product artifacts.
2. Prepare one cohesive integration design/test package: original-source reverse matrix, exact bounded product replacements and durable mismatch resolution, static connected caller flows, fault-injection boundaries and complete historical/current integrity checks.
3. Obtain independent design-freeze PASS; root corrects all findings with focused follow-up before product cleanup.
4. Apply only reviewed product deltas, synchronize Generator export, verify unchanged Validator pair and every protected path. Run complete S5 integration/artifact gate.
5. Obtain independent whole-stage review on all criteria; root corrects findings and obtains focused PASS as required.
6. Reconcile exact evidence/hashes and Git state, close S5 and the repository roadmap. Record one concrete handoff next action without claiming Pega runtime or creating an unauthorized commit/push.

## Progress

- VERIFIED — startup Git state matches committed S4; only .idea/ is untracked. Effective legacy search and S1/Author envelope inspection identified bounded integration cleanup surfaces.
- VERIFIED — milestone1 activation received prescribed-profile independent PASS and root reconciliation.
- VERIFIED — milestones2–3 cohesive design and corrected independent freeze PASS are reconciled.
- VERIFIED — milestones4–6 are complete: reviewed products, full current/historical gate, independent whole-stage PASS and root closure reconciliation on2026-09-08. S0–S5 are CLOSED.

## Acceptance Criteria

1. VERIFIED — Activation and cohesive design each receive independent actual gpt-6-astra/xhigh PASS and root reconciliation.
2. VERIFIED — All150original rows have exact source clauses, one accountable authority, complete distinct effective roles, current destinations and test/audit evidence; no orphan or conflicting semantic duplication remains.
3. VERIFIED — MemoryTemp, CreateAIAgentResponseRecord and GetAIAgentResponseRecord are absent from all five effective deliverables; every removal/replacement is bounded and justified without loss of stable gates. Excluded Main_Agent.txt remains fixed.
4. VERIFIED — Author, Generator and Validator expose only intended interfaces and responsibilities; code allowlists and prompt/export metadata agree. Author envelope handling conforms to S1 and full SIM trace/provenance ownership conforms to DEC-016/030.
5. VERIFIED — Sequential source writes/handoff/read order preserve exact CaseID, original RUTType, opaque UUIDs, source payload bytes and immutable source/group membership. No source retry, partial handoff, inline Payload or latest-record path exists.
6. VERIFIED — Both schema families complete through the connected real Generator/Validator oracles and full schemas, including more than one physical When group where appropriate; candidate history is immutable and final success identifies only current validated UUID.
7. VERIFIED — Partial success, isolated Scenario rejection, shared When-group rejection, all-failed and candidate-wide stop produce consistent counts/outcomes/current coordinates and preserve original source identities and values.
8. VERIFIED — Repair writes a new candidate version, Validator schema/read inspect that exact UUID, total repair attempts never exceed two, and write/transport failure cannot expose an older candidate as success.
9. VERIFIED — Wrong CaseID/Type/UUID, malformed responses, schema invalid/tool failure, Memory failure and absent Knowledge short-circuit correctly; no unapproved agent/tool call occurs.
10. VERIFIED — Author maps Generator Completed/PartiallyCompleted to exact external Completed and Failed to exact external Failed, detects malformed reports and preserves bounded two-field errors without leaking UUIDs/payloads.
11. VERIFIED — Both selected prompt/export pairs decode exactly; current artifacts reconstruct deterministically from fixed baseline and approved replacements; all unrelated metadata, source/contracts/schemas/fixtures/implementations and excluded Main export remain fixed.
12. VERIFIED — Historical full S4 gate (including all S2/S3 suites) passes on fixed isolated baseline. Current S5 integration, reverse matrix, complete legacy search, artifact/protected-scope, link/next-action, whitespace and meaningful negative mutations also pass.
13. VERIFIED — Independent whole-stage actual gpt-6-astra/xhigh PASS has no remaining actionable findings; root records current hashes, correction history and honest static limits and closes S5 with one synchronized handoff action.

## Validation

- Use Python with the unchanged requirements-s3.txt; full Draft202012Validator, not a partial schema substitute.
- Run fixed historical `python -B scripts/validate_s4_design.py` in an isolated local checkout of d4061046650c87b9da2c4f87141f23aa2602f082. Verify that checkout's HEAD and exclude its generated caches from the real repository.
- Add `python -B scripts/validate_s5_integration.py` and a complete `python -B scripts/validate_s5_design.py` gate. Use all existing real parser/projection/consumer components, schema validation for actual candidates/reports, explicit per-agent call logs and assertion-rich fault controls.
- Prove fixed source/semantic snapshots unchanged before/after every fault/repair; do not assert source audit passes on a deliberately corrupted candidate. Audit ordinary projections before injection and final successful survivors afterward.
- Exact baseline-restoration/current-hash checks supplement preserved historical tests; positive and negative tests must reject extra interface/legacy/reference/path/metadata drift and wrong-version success.
- Independent reviewers are read-only actual gpt-6-astra/xhigh; root is sole writer. No product work before design PASS or stage closure before whole-stage PASS.

## Evidence

- VERIFIED — on 2026-09-08 root created the user-authorized local S5 closure checkpoint in 22 project paths, with vkoloskov <95134563+vkoloskov@users.noreply.github.com> as both author and committer. Parent is d4061046650c87b9da2c4f87141f23aa2602f082; main is four commits ahead of unchanged local origin/main and only .idea/ remains untracked. The complete staged S5 gate passed, including 16 integration groups and the fixed historical S4/S3 gate (35 producer groups, seven suites/180 corrections). This same checkpoint includes its Git-state reconciliation; resolve its final self-referential hash from Git. No push was performed; all S0–S5 stages remain CLOSED.

- VERIFIED — on 2026-09-08 the user authorized a local S5 closure commit. The previously selected identity remains vkoloskov <95134563+vkoloskov@users.noreply.github.com> for both author and committer. Include the verified S5 project changes and Git-state reconciliation; exclude .idea/. All S0–S5 stages remain CLOSED. No push is authorized.

- VERIFIED — on2026-09-08 /root/review_s5_closure actual gpt-6-astra/xhigh returned whole-stage PASS with no actionable findings. Reviewer independently passed16connected groups,150rows/36current-role additions,85protected paths, eight artifact/four matrix mutations, both-pair parity/metadata/hashes and the full fixed historical S4/S3 gate (35producer groups, sevenS3suites/180corrections), plus five additional read/write/handoff/metadata/duplicate-JSON probes. Root reconciled all13criteria, exact current artifact manifest, Git state and static evidence limits. S5 is VERIFIED and CLOSED; all S0–S5 repository stages are CLOSED. S5 remains uncommitted; no push or Pega import/runtime occurred.

Earlier entries below retain their checkpoint state; the latest closure entry and plan status govern current readiness.

- IMPLEMENTED_NOT_VERIFIED — the complete current S5 artifact gate passed after product application:16connected integration groups, eight artifact/four reverse-audit mutations,150original rows/36explicit current consumer additions,85protected files and both decoded pairs. The unchanged full S4 gate passed on the isolated fixed S4 checkout (35producer groups, sevenS3suites/180corrections). Current product hashes are recorded in fixtures/s5/artifact-manifest.json and the S5 acceptance report. Whole-stage independent PASS and root closure reconciliation are pending.

- IMPLEMENTED_NOT_VERIFIED — the reviewed S5 product overlay is now applied in exactly Main_Agent_Prompt.txt, UnitTestGenerator_Prompt.txt and UnitTestGenerator.txt. The builder confirms all nine replacements plus the report reference, exact decoding of both selected pairs, absence of legacy names and byte-identical Generator metadata. Validator pair and85protected baseline files are unchanged. The current full integration/artifact gate and independent whole-stage review are the remaining gates; no commit/push or Pega runtime occurred.

- VERIFIED — focused /root/review_s5_design actual gpt-6-astra/xhigh returned design-freeze PASS with all three P2 findings closed and no remaining actionable findings. Reviewer independently passed the complete16-group design gate, eight artifact/four reverse-audit mutations,150rows/85protected files, fixed historical S4/S3 gate and18additional schema-valid multi-group terminal-report probes. Root reconciled unchanged product baseline and complete local gate. The nine bounded runtime replacements and report-only G9 reference may now be applied; whole-stage closure remains pending.

- IMPLEMENTED_NOT_VERIFIED — /root/review_s5_design actual gpt-6-astra/xhigh returned FAIL with three P2 groups. Root corrected the executable Section13 extra-metadata contradiction, added36current consumer responsibilities with real prompt anchors and full destination/Markdown checks, and implemented report-only G9 consistency/known handoff binding. The focused gate passes16integration groups,13schema-valid report mutations in object/raw forms, four reverse-audit negative controls, eight artifact mutations and85protected files. Nine exact product replacements are proposed; actual products remain fixed. Historical full gate previously passed locally and independently; this focused run did not repeat it. Focused independent design PASS remains required.

- IMPLEMENTED_NOT_VERIFIED — cohesive S5 design now includes DEC-031/S5_INTEGRATION.md, eight exact runtime replacements plus existing terminal-report reference, all150reverse rows,85fixed protected baseline paths, deterministic proposed artifacts, a static Author storage adapter and connected real Generator/Validator flow harness. The complete design gate passes15integration groups, both-pair proposed parity/seven artifact mutations and the unchanged full S4 gate on an isolated fixed S4 checkout, including35producer groups and sevenS3suites/180corrections. Actual product bytes remain unchanged; independent design-freeze PASS is required before applying the overlay.

- VERIFIED — /root/review_s5_activation used actual gpt-6-astra/xhigh and returned PASS with no activation findings. Independent full S4 gate, fixed Git/product state, all13criteria, local links and synchronized next action passed. Root reconciled the report and activates S5. Design must explicitly supersede the protected historical ScenarioGroup §17 extra-field rejection as well as Main §1A through the S1-consistent S5 interpretation; source grammar remains unchanged.

- VERIFIED — activation Git HEAD d4061046650c87b9da2c4f87141f23aa2602f082 and only .idea/ untracked were observed on2026-09-08.
- VERIFIED — legacy names survive in Main/Generator prohibitions and overridden source text; Validator pair is already clear. Original S1 allows platform metadata, while Main Section1A currently rejects extra fields. These findings define review surfaces, not an already verified correction.
- IMPLEMENTED_NOT_VERIFIED — this plan requires independent activation review. No S5 runtime/integration PASS is claimed.

## Risks

- Activating the final stage changes operational state and requires milestone1 independent review.
- Reverse authority mappings, Author envelope reconciliation, trace ownership wording and cleanup replacements are a cohesive high-risk design batch, gated by milestone3 before product edits.
- Broad historical-gate exceptions can hide regressions. Fixed isolated baseline plus unchanged code/contract census and exact current-product deltas must remain independently reviewable; do not weaken earlier tests to obtain PASS.
- Fault-injected fixtures are not a Pega runtime or proof of arbitrary semantic reasoning. Static adapter and historical tests must have explicit evidence boundaries.
- Product cleanup is high-risk; milestone5 must audit original clauses, both-pair parity, metadata scope and full actual caller flows before closure.

## Exact Next Action

Await user-owned Pega import/runtime results for the committed S5 artifacts.

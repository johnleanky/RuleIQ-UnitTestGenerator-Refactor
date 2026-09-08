# ExecPlan: S4 Validator Refactor

- **Roadmap stage:** `S4`
- **Plan status:** `CLOSED` — independent whole-stage PASS on all 14 criteria and root reconciliation complete, 2026-09-08.
- **Last reconciled:** 2026-09-08

## Purpose

Refactor UnitTestValidator to inspect exactly the candidate UUID supplied by UnitTestGenerator, preserve the existing alignment and documented Pega behavior checks, and emit the already verified S3 consumer report. Finish S4 with an independently verified canonical prompt and synchronized existing agent export. Do not activate S5.

## Scope

- Refactor `Validator_Prompt.txt` and the paired `JsonValidator_tool.txt` Rule-AI-Agent export. Keep the existing rule identity and model. Limit export changes to the system prompt, directly affected response style, named tool references and their corresponding reference metadata. Replace the legacy candidate read with a named GetMemory reference; do not invent external backing configuration.
- Create a complete S4 instruction slice covering all 44 IPM-VAL rows and the Validator-owned/shared Author obligations relevant to validation. Preserve every stable source clause, identify accepted legacy removals, and bind each effective row to concrete executable checks and prompt destinations.
- Freeze a self-contained Validator producer contract aligned with S1 and the unchanged S3 report schema/catalog. Define exact input/envelope checks, schema-first short circuits, mass-error handling, all-unit RUT checks, one UTC lookup, trace/RuleCode alignment, documentation checks, scope and route precedence.
- Add repository-only producer fixtures/oracles, malformed-response and mutation regressions, report-schema/Generator-consumer compatibility tests, deterministic prompt/export integrity and bounded metadata-diff checks. Exercise real S3 candidates for both schema families without pretending to run Pega.
- Adapt the historical S3 gate only as needed for the active-plan pointer and the two explicitly selected Validator artifacts; preserve fixed S3 artifact hashes, all suites and checks of every other protected file. Any scope exception must be fixed, justified and covered by the S4 gate, not silently disable preservation checks.

## Excluded Scope

- Author or Generator semantic changes, source revisions, candidate schemas/examples, Knowledge Areas, external tool implementation, target Ruleset/Version selection, live Pega import/runtime or remote mutation.
- `Main_Agent.txt` edits or parity checks. It remains reference-only under DEC-017.
- S5 full integration/legacy cleanup and push. The original S4 request authorized repository work through closure; the user subsequently authorized the local S4 closure commit on 2026-09-08 under the same vkoloskov identity.
- New RUT analysis, dependency discovery, expected values, assertions or simulation payloads; candidate writes, repairs or persisted reports by Validator.

## Assumptions and Unknowns

- At S4 activation, HEAD was `4393c680633d176129676f7b91179262cc25391f`, parent `8509a508ee586136b4a06caa86ee50a51a391b0e`; `main` is two commits ahead of unchanged local `origin/main` at `4161fd3f77fc562ecb1e9fded19b5391ea67722f`. Only pre-existing `.idea/` is untracked at activation.
- S0–S3 are CLOSED. The historical Validator source is available both at S3 HEAD and `b9dd565`; original matrix line references refer to that unchanged source. Current S3 artifacts and contracts are the consumer authority.
- S1 defines JsonValidationTool Success/IsValid/ValidationMessage/ErrorCode/ErrorMessage and GetMemory Success/Payload/ErrorCode/ErrorMessage. A boolean IsValid alone is insufficient. Addresses are opaque and passed unchanged.
- Validator trusts the candidate trace as the mechanical projection of frozen decisions; Generator owns comparison with ScenarioGroups. Validator must not read source groups or invent absent evidence to fill information not present in candidate JSON. Any source-information limitation discovered during design is recorded and resolved without guessing.
- The existing report schema permits the required routes/codes/actions. New interpretations of underdetermined diagnostics, normalization or unavailable documentation require explicit evidence and independent design review before product implementation.
- Pega references, backing-tool behavior and import/runtime remain external and UNKNOWN under DEC-019. Local validation uses Python with the already pinned `requirements-s3.txt` and full Draft 2020-12 support.

## Dependencies

- [Roadmap](../ROADMAP.md), [continuity and reviewer gate](../CONTINUITY.md), [decisions](../../decisions/DECISIONS.md), especially DEC-001–008/011–012/016–019/023–024/028–029.
- [S0 preservation matrix](S0-baseline-contracts.md), [closed S3 plan](S3-unit-test-generator.md), [S3 acceptance](../design/S3-acceptance-report.md).
- [S1 caller contract](../../contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md), [Generator consumer contract](../../contracts/UNIT_TEST_GENERATOR_V1.md), [report schema](../../contracts/VALIDATOR_REPORT_S3.schema.json), [ScenarioGroup 1.3](../../contracts/SCENARIO_GROUP_V1.md).
- [S4 acceptance report](../design/S4-acceptance-report.md) records verified artifact hashes, static results, whole-stage PASS and all 14 satisfied criteria.

## Milestones

1. Independently review activation plan and reconcile Git/source scope. Activate S4 only after prescribed-profile PASS and root reconciliation.
2. Prepare one cohesive design package: complete instruction slice, producer contract, trace/behavior rules, exact report catalog/scopes, observed export change boundaries, regression-gate adaptation and independent protocol/alignment fixtures. Record durable interpretations in decisions.
3. Obtain independent design-freeze PASS. Root alone corrects findings; any high-risk corrections require focused follow-up before dependent product changes.
4. Implement canonical Validator prompt and targeted existing export synchronization from the verified design. Add artifact manifest, deterministic builder/parity and protected-metadata checks. Run producer, alignment, report and complete S2/S3 regression gates.
5. Obtain independent whole-stage review against every acceptance criterion and original clauses. Correct all actionable findings and obtain focused PASS where required.
6. Reconcile verified evidence, close S4, update Roadmap and continuity, and retain exactly one next action for S5 activation preparation. Keep S5 NOT_STARTED; do not commit/push without new authorization.

## Progress

- `VERIFIED` — startup Git state matches the S3 checkpoint; only `.idea/` is untracked. S1/S3 calls, all 44 Validator source rows, existing tools and output surfaces were inspected read-only.
- `VERIFIED` — milestone 1: `/root/review_s4_activation` actual gpt-6-astra/xhigh PASS; root corrected the closed-plan label and reconciled unchanged product state and complete separate S3 baseline. S4 is ACTIVE.
- `VERIFIED` — milestones 2–3: complete corrected design received prescribed-profile PASS and root reconciliation.
- `VERIFIED` — milestones 4–5: canonical Validator prompt/export, complete artifact gate and focused whole-stage gpt-6-astra/xhigh PASS; all original and residual findings corrected.
- `VERIFIED` — milestone 6: all 14 acceptance criteria satisfied, exact evidence/hashes reconciled, S4 CLOSED and S5 NOT_STARTED; no commit or push.

## Acceptance Criteria

1. Activation and design each receive gpt-6-astra/xhigh independent PASS and root reconciliation.
2. Every one of 44 IPM-VAL rows and relevant Validator-owned/shared Author obligations has exact original-source traceability, justified disposition, prompt destination and executable regression; no stable clause is lost or semantic ownership duplicated.
3. Input gate validates CaseID, immutable RUTType and current UnitTestCandidateUUID before tools; schema and UTC keys derive solely from original RUTType; caller-supplied schema is ignored.
4. One schema call passes exact CaseID/UUID/schema. All failed/malformed envelopes and invalid content short-circuit correctly before Memory/Knowledge/alignment. Ordinary and 25-error/broad-shape/oversized failures produce bounded compatible reports.
5. Only schema success permits one exact candidate GetMemory read with the same UUID and Type=UnitTestCandidate; no retries, latest lookup, source read, write or persisted report exists.
6. All current units receive immutable-RUT metadata checks before one complete UTC lookup for either family; unusable documentation stops safely.
7. Full DEC-016 ASSERT/SIM/OMIT grammar, sig/params and all omission reasons are preserved. Entity/single-string-layer normalization and canonical paths do not manufacture semantic equivalence or change candidate bytes.
8. Bidirectional assertion, omission and simulation correspondence, explicit supports, visible counts, Param/Page/List/ResultCount shapes and trace-only path repair remain effective. Missing/contradictory decisions route to semantic rejection.
9. MultInpComb preserves one-based row/current Scenario correspondence, cell bijection/signature/order, Result last, exact nested paths/labels, initialized empty input and reserved-page checks; shared failures use group scope.
10. Documentation checks preserve all original behavior checks and synthetic IsInPageListWhen contradiction handling without reimplementing strict schema validation or deriving RUT semantics. Unsafe ambiguity routes HUMAN.
11. Every report conforms to the unchanged closed S3 schema/catalog and Generator semantic consumer: exact counts, valid flag, HUMAN > SEMANTIC_REJECT > GENERATOR_REPAIR > OK, warning-only behavior and current candidate coordinates. Mixed issues are assessed atomically.
12. Canonical prompt/export decode exactly, contain self-contained runtime instructions/schema and only allowed named tools; all export bytes outside the explicitly approved regions and every unrelated product/S1/S3 contract are preserved.
13. Full S2/S3 regressions and meaningful S4 positive/adversarial producer, alignment, both-family candidate, route/scope and artifact tests pass. Tests are repository-static evidence, not a Pega invocation.
14. Independent whole-stage gpt-6-astra/xhigh PASS has no remaining actionable findings; root records exact evidence/hashes, closes S4 with S5 NOT_STARTED and one synchronized next action.

## Validation

- Resolve repository root from the script/checkout, keep repository documentation paths relative, preserve `.idea/`, inspect Git status/diff and both staged/unstaged whitespace.
- Run `python -B scripts/validate_s3_design.py` with `requirements-s3.txt` before changes; keep its complete seven-suite regression coverage after the narrowly reviewed S4 adaptation.
- Add `python -B scripts/validate_s4_design.py` as the complete S4 gate. Use real both-family S3 projection fixtures plus independently constructed mismatches; inspect all tool-call sequences and validate every produced report against the full Draft 2020-12 report schema and existing Generator consumer.
- Prove prompt/export parity and exact bounded export restoration to activation HEAD; verify fixed hashes for Author/Generator/source/report contracts and all excluded artifacts. Mutation probes must reject omitted clauses, broadened allowlists, wrong UUID/order, altered values, malformed traces, stale scopes and metadata drift.
- Check complete row census, original source clauses, report examples/catalog/schema parity, local documentation links, a single synchronized active-plan next action, and no generated caches.
- Independent reviewers are read-only and use explicit `gpt-6-astra` / `xhigh`; no silent substitution. Root is sole writer and reconciles every result.

## Evidence

- `VERIFIED` — on 2026-09-08 root created the user-authorized local S4 closure checkpoint in 20 project paths and verified both author and committer as vkoloskov <95134563+vkoloskov@users.noreply.github.com>. Parent is S3 checkpoint 4393c680633d176129676f7b91179262cc25391f; main is three commits ahead of unchanged local origin/main and only .idea/ remains untracked. The complete staged S4 gate passed, including 35 producer groups and all seven S3 suites/180 corrections. This same local checkpoint includes its Git-state reconciliation; resolve its final self-referential hash from Git. No push was performed. S4 stays CLOSED, S5 NOT_STARTED and the synchronized next action is unchanged.

- `VERIFIED` — on 2026-09-08 the user authorized the local S4 closure commit. The inherited checkpoint identity is vkoloskov <95134563+vkoloskov@users.noreply.github.com> for both author and committer. Include the verified S4 project changes and Git-state reconciliation; exclude .idea/. S4 remains CLOSED and S5 NOT_STARTED with the same next action. No push is authorized.

- `VERIFIED` — final focused /root/review_s4_closure actual gpt-6-astra/xhigh returned whole-stage PASS with no remaining actionable findings. All original and focused corrections are closed. Reviewer independently passed 76 schema-valid scalar producer/consumer probes, five ASCII/Unicode blank-RUT cases, both-family opaque-address controls and the complete 35-group S4 gate with seven S3 suites/180 corrections, 150/73 dispositions, 57 protected artifacts and 10 reports. Root reconciled exact product hashes/parity, bounded export restoration, metadata, links, Git state and evidence limits. All 14 S4 criteria are VERIFIED; S4 is CLOSED on 2026-09-08, S5 stays NOT_STARTED. S4 changes are uncommitted; no commit/push or Pega import/runtime was performed.

- `IMPLEMENTED_NOT_VERIFIED` — focused whole-stage review confirmed both original findings corrected and found one residual supported String-mode omission. Root added String to the scalar gate and runtime V6; an independent explicit eight-mode census now drives schema-valid true/false positive, physical mismatch, invalid-decision and missing-target controls. Other source typing and opaque-address boundaries remain unchanged. Focused PASS is still required.

- `IMPLEMENTED_NOT_VERIFIED` — whole-stage /root/review_s4_closure actual gpt-6-astra/xhigh returned FAIL with two P2 groups. Root corrected explicit scalar constraints before physical matching (including missing targets), Text/native-boolean comparison and blank RUTType zero-call handling without modifying opaque addresses. V1/V5/V6, row regressions and product pair are synchronized. New schema-valid positive/adversarial cases preserve arrays/null source limits and current decision scopes; all 35 producer groups pass. Focused whole-stage PASS is required before closure.

- `IMPLEMENTED_NOT_VERIFIED` — the bounded Validator product batch is implemented. Canonical prompt embeds V1–V10 plus the unchanged closed report catalog/schema and 10 examples. Export synchronization changes only the approved prompt/read-tool/reference regions; exact decoding, deterministic reconstruction, complete baseline restoration and four negative artifact probes pass. Full S4 artifact gate passes (33 producer groups, 150/73 dispositions, 57 protected files, 10 reports, all seven S3 suites/180 corrections). Whole-stage independent review is pending; S5 remains NOT_STARTED.

- `VERIFIED` — final focused `/root/review_s4_design` actual gpt-6-astra/xhigh returned design-freeze PASS with no remaining findings. Reviewer independently confirmed all original/focused fixes, 12 extra type/quote/numeric/boolean controls, 33 groups, 150/73 dispositions, 57 protected files, 10 reports and seven S3 suites/180 corrections. Root reconciled unchanged Validator baseline and all gates. Product implementation may proceed; S4 closure and runtime remain unverified.

- `IMPLEMENTED_NOT_VERIFIED` — second focused review confirmed the prior four fixes but exposed mixed Text/Decimal order dependence in final-ledger equality. Root now requires compatible explicit typing on both decisions before numeric equivalence and keeps canonical text/When comparisons exact. Both mixed-type orders reject; Decimal 1/1.0 compatibility passes in both orders. The producer suite has 33 groups; focused PASS remains required.

- `IMPLEMENTED_NOT_VERIFIED` — first focused S4 review confirmed the original seven groups corrected and found four residual P2 cases: asymmetric quote fallback between final trace values, literal OMIT paths, consumed exact-target multiplicity, and quoted diagnostic values mistaken for counts. Root separated canonical decision comparison from legacy candidate fallback, preserved literal OMIT and exact-target interpretation, restricted reported-count recognition, and added both-order/negative controls. All 32 producer groups and the complete S4 design gate (including seven S3 suites/180 corrections) pass; focused PASS remains required before product creation.

- `IMPLEMENTED_NOT_VERIFIED` — `/root/review_s4_design` actual gpt-6-astra/xhigh returned FAIL with seven P2 groups: final-decision contradictions, quote/path normalization, observable property/When context, simulated DP roots, mass diagnostics and traversal-before-Knowledge. Root corrected the cohesive batch, synchronized V3/V5–V8 and added all reported positive/negative probes. The producer suite passes 29 named groups and the complete S4 design gate passes with all seven S3 suites/180 historical corrections, 150 rows, 57 protected paths and 10 report examples; focused independent PASS remains required. Product pair is unchanged.

- `IMPLEMENTED_NOT_VERIFIED` — S4 cohesive design batch now includes the V1–V10 producer contract/DEC-030 evidence boundary, 150-row preservation slice (73 effective: 43 retained Validator plus 30 Author obligations), 57 fixed protected owner artifacts, 24 adversarial protocol/alignment groups, 10 full-schema/consumer report examples, export change boundary and narrow S3 gate adaptation. Complete S4 design gate and all seven S3 suites pass locally, including 180 historical correction regressions. Product Validator pair remains byte-identical to S3 HEAD. Independent design-freeze review is pending; product implementation is stopped.

- `VERIFIED` — activation reviewer confirmed scope, gates, S1/S3 boundaries, 44-row preservation plan, current links/next action and unchanged non-documentation files. Root separately passed all seven S3 suites and matrix/scope/future-tracking/report/artifact checks; historical S3 docs() requires the planned active-pointer adaptation.

- `VERIFIED` — 2026-09-08 `git status --short --branch` reports main ahead 2 and only `.idea/` untracked; `git log -2` shows S3 closure `4393c68` and preparation `8509a50`.
- `VERIFIED` — original Validator allowlist has JsonValidationTool, GetAIAgentResponseRecord and KnowledgeTool; the existing export is Rule-AI-Agent UnitTestValidator with corresponding reference rows. These are the selected replacement surfaces, not new backing-tool implementations.
- `IMPLEMENTED_NOT_VERIFIED` — this plan is ready for activation review. No S4 implementation or runtime result is claimed.

## Risks

- Activation changes operational state; milestone 1 gates it independently before design work.
- Interface, trace normalization, scoping and route changes are one high-risk design batch. Milestones 2–3 require original-clause review and malformed/adversarial coverage before prompt creation.
- Candidate-only Validator lacks source ledgers; do not fabricate verification of fields absent from RuleCode/trace. Resolve limitations explicitly during design while retaining Generator's source audit.
- S3 gate assumptions currently point at the closed S3 plan and protect legacy Validator bytes. Narrow adaptations must retain historical fixed baselines and test all other protections.
- The prompt/export batch is high-risk; milestone 5 must verify self-contained instructions, exact metadata boundaries and producer/consumer compatibility before closure.
- Repository-static tests cannot prove external tool isolation, active Pega configuration or imported agent behavior. S5 remains a separate stage.

## Exact Next Action

Prepare the S5 integration activation ExecPlan for independent review; keep S5 NOT_STARTED until activation is verified.

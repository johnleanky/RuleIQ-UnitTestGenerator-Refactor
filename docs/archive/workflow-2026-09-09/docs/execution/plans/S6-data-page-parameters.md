# S6 — Data Page Parameter Resolution

## Purpose

Implement the user-approved Data Page binding correction and ScenarioGroup revision 1.4, preserving the three-agent ownership boundary.

## Scope

Data Page KnowledgeArea; Author and Generator prompts; Generator prompt export; revision-aware source checks; explicit, inherited, default and empty-map fixtures; connected static caller flows; instruction traceability and current artifact preservation.

## Excluded Scope

The broader initial-scenario locking redesign, Model WHEN field mapping, STRING alias correction, Data Page root assertions and the two existing Validator findings remain separate. Main_Agent.txt, candidate schemas, tool signatures and Validator products remain unchanged. No Pega deployment or runtime verification.

## Assumptions and Unknowns

The user confirms implicit same-name current-Param binding for declared Data Page inputs in this RuleIQ environment. This is not universal Pega behavior. Unknown declaration field mappings remain unresolved. Fixtures label extracted metadata and expression evaluations as synthetic; they do not claim verified Pega extraction.

## Dependencies

S0–S5 closed; baseline 13b44c7f59c250d3a54fb11d4dfb6ecbb5db24a8. DEC-033 and the S6 contract govern only this bounded change. Existing historical contracts and fixtures remain fixed evidence.

## Milestones

1. Establish stage and exact revision-1.4 evidence contract; independent read-only design/activation review.
2. Implement the cohesive prompt, parser, evidence-check and fixture batch; stop dependent work for independent review.
3. Reconcile corrections, run complete current and fixed historical checks, and close after independent PASS.

## Progress

- IMPLEMENTED_NOT_VERIFIED — stage and source evidence contract prepared for independent design review. No product changes yet.
- IMPLEMENTED_NOT_VERIFIED — first gpt-6-astra/xhigh review returned FAIL on unknown access state, incomplete current-state/producer proof and null carrier wording. Root added explicit UNKNOWN gaps, complete derived caller-state checks and exact null/empty/absent carriers; focused review pending.

## Acceptance Criteria

1. KnowledgeArea owns explicit/current-Param/default resolution, unknown versus empty declarations, timing and caller-versus-loader distinction; Thread eligibility is preserved.
2. Author captures symbolic producers before concrete execution, does not seed RUT-produced values, and preserves scenario membership during parameter refinement.
3. Revision 1.4 enforces access/declaration provenance, exact typed parameter matching, default mode, and evidenced zero-parameter SIMs. Older source revisions are rejected by current consumers.
4. Generator source audits precede projection; candidate-only Validator boundaries and all external tool/candidate shapes remain unchanged.
5. Positive and adversarial fixtures cover explicit, implicit, default, unresolved, skipped, overwritten, repeated-access, typed and parameterless cases, plus the supplied GetCaseData branch simulation.
6. Connected static flows prove immutable Memory handoffs and schema-valid candidates. Frozen historical suites remain passing at the baseline.
7. Prompt/export parity and unchanged export metadata pass; every bounded instruction delta has traceability, all unrelated baseline artifacts remain unchanged, and independent required-profile review returns PASS.

## Validation

Run `python -B scripts/validate_s6_parameters.py` for current source, semantic fixture, connected flow and preservation checks; `python -B scripts/validate_s6_parameters.py --historical` additionally runs the unchanged S5 gate in an isolated fixed-baseline checkout. Run `git diff --check`. Reviewer uses gpt-6-astra/xhigh, read-only.

## Evidence

Initial Git inspection: main, HEAD 13b44c7, clean worktree. Existing parser rejects absent SIM.parameterResolutions and PARAM mode=default; Generator reads only revision 1.3. KDP.1–3 contain no binding rules.

## Risks

Activation/design and the cohesive implementation batch are high risk and require independent review before dependent work. Static snapshots validate consistency, not arbitrary RUT evaluation or actual Pega metadata. Historical gates must run at fixed commits rather than rewriting closed expectations. The original supplied RUT's unrelated known defects prevent claiming its complete end-to-end readiness.

## Exact Next Action

Obtain independent read-only S6 design/activation review and reconcile findings before product implementation.

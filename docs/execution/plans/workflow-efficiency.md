# Workflow Efficiency

Execution state and the next action are owned by [continuity](../CONTINUITY.md).

## Scope and decisions

Implement [DEC-034](../../decisions/DEC-034.md): compact startup context, single ownership of current state, on-demand history/decisions and one independent review per cohesive high-risk batch. Preserve exact pre-migration management snapshots and all unrelated product, schema, export, contract and historical-plan bytes. S6 design verification must remain distinct from pending implementation.

## Interfaces

Startup is AGENTS + continuity + the active plan. Limits are 2,000/3,500/6,500 characters respectively and 12,000 combined. Continuity uses labeled Objective, Stage, Active plan, State, Baseline, Verified evidence, Pending, Blockers, Context and reviews fields, followed by exactly one Exact next action. Plans hold scope, acceptance and validation, never duplicate current state or next actions. Decision index links to individual entries; archived raw links resolve relative to their original source paths documented by the archive.

## Acceptance

1. Every old management snapshot matches its recorded SHA-256; all old decision entries remain retrievable and historical evidence links retain meaning.
2. Startup stays within each size limit and has valid local links, required fields, one next action and no contradictory active-stage state.
3. The checker rejects missing evidence links, absent files/anchors, duplicate next actions, malformed state fields and exceeded budgets.
4. Product/contract/schema/export bytes and historical plans remain unchanged from the pre-migration capture; preserve the pre-existing S6 work.
5. One independent gpt-6-astra/xhigh review passes, with focused correction review if needed. Record measured startup size and review count; do not claim token telemetry.

## Validation

Run `python -B scripts/check_project_state.py --self-test --migration` and `git diff --check`. The migration flag verifies archived snapshots, decision census/extraction and the preserved pre-migration file manifest; it is a bounded migration gate, not a future prohibition on authorized product changes. Default checker remains applicable to future work. Full product suites are not required for this documentation/checker-only batch because product and original test bytes are verified unchanged.

## Risks and recovery

This governance change is high risk and requires independent review before VERIFIED. Keep original evidence byte-identical and accessible; derived summaries cannot supersede technical contracts. The checker validates structured management facts and links, not arbitrary semantic claims. Resume S6 after closure; no product implementation, commit, push or Pega action is included here.

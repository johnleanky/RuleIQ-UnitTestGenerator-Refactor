# Workflow Policy

Authority: [DEC-034](../decisions/DEC-034.md), accepted by the user on 2026-09-09. This policy replaces duplicated next-action/state records and mandatory activation/design/closure review sequences. Historical records remain evidence of their original process, not current operating instructions.

## Ownership and loading

AGENTS provides startup rules. Continuity owns current objective, stage, state, blockers, verified evidence and the sole next action. The active plan describes scope, interfaces, decisions, acceptance and commands; it links to continuity for execution state. The roadmap is a stage index. Individual decisions own durable choices. Technical contracts retain their necessary detail.

At startup read only AGENTS, continuity and its active plan, inspect Git and reconcile material discrepancies. At compaction reload compact state and active plan. Follow contract/decision links only when relevant. Preserve history, archives, decisions and evidence; open them only for a specific question. Search before bounded reads. Context budgets govern summaries, never truncation of technical evidence. Root alone updates global continuity. Record one compact checkpoint per completed batch or blocker with links to details. Reuse the approved plan and inspected source until they change; replan only for material conflicts or scope changes. Default tool output to 1,500 tokens; expand deliberately for necessary content. Successful checks return one summary line; failures return relevant diagnostics. Routine updates use 1-2 sentences. Avoid repeating findings across updates, reports and handoffs. Use existing serializers/checkers for mechanical work and continue approved implementation without another planning/activation cycle.

## Risk and independent review

High risk includes changes to agent instructions, behavior, schemas, KnowledgeAreas, tool/Memory interfaces, grouping, assertions, simulations, repair/routing policy, broad rewrites, and workflow policy. Complete the entire approved refactoring batch, including its workflow edits, and run the required gate before one independent read-only project review. Eliminate separate workflow, activation, design and closure reviews within that batch. Resolve architectural ambiguity during implementation planning without adding a review milestone. Stop dependent work at final review until findings are reconciled.

Every required independent reviewer uses explicit `model=gpt-6-astra`, `reasoning_effort=xhigh`. If unavailable, mark the gate BLOCKED and request direction; do not silently substitute. Routine documentation maintenance uses root checks. Governance changes that alter controls remain high risk.

Send a concise review packet: baseline/diff, affected paths, invariants, acceptance criteria and test evidence. Use no full chat-history fork. Reviewer retrieves additional context as needed and reports actionable findings and PASS/FAIL/BLOCKED. Root applies corrections and obtains a focused recheck of affected behavior; repeat the full review only when scope materially expands. Blocking findings prevent VERIFIED status and work depending on the affected behavior. One final review satisfies batch/stage closure. An interrupted review is incomplete, not PASS; preserve its findings and resume the unfinished review.

## Validation and evidence

Run checks relevant to each change, then the complete gate defined by the active plan before closure. Preserve historical gate inputs; do not rewrite closed expectations to obtain PASS. Reuse earlier results only when the files, inputs, configuration and environment they cover remain applicable. Link one compact evidence record containing commands, outcomes, evidence scope, relevant baseline/file identities, review count and startup-character count. Record actual tokens only when telemetry exists; character counts are context-size proxies.

States: NOT_STARTED means no implementation; IMPLEMENTED_NOT_VERIFIED means changes exist but mandatory checks/review remain; VERIFIED means required evidence and independent PASS for high-risk work have been reconciled; PARTIAL means incomplete scope; FAILED means a failed check; BLOCKED means an external dependency or decision prevents progress; UNKNOWN means insufficient evidence. Distinguish design verification, repository-static validation and Pega runtime verification. Preserve material failures and their resolution once rather than repeating their chronology across documents.

## Product safeguards

Readable *_Prompt.txt files are canonical. Synchronize only selected export pairs and intended pySystemPrompt content; verify decoded parity and unchanged external metadata. Main_Agent.txt is reference-only. Preserve KnowledgeArea marker IDs, schema family names/casing, opaque Memory/UUID contracts and instruction-to-owner traceability. Maintain a bounded delta mapping, not a duplicated full matrix. Schema changes must pass their matching examples. Project-review timing does not change RuleIQ runtime UnitTestValidator behavior. Pega tools and target selection remain external; consult applicable contracts before changing those interfaces.

## Closure and recovery

Check acceptance, complete the required gate, reconcile independent findings, and update continuity once. Keep evidence and review conclusions in the linked batch record. Historical plans retain their original next actions as archival text; only current continuity has operational authority. At transition update the roadmap index and select the next active plan without creating a separate activation review. Run `python -B scripts/check_project_state.py` at handoff. It checks structural consistency and budget, not truth of arbitrary prose or actual Pega behavior.

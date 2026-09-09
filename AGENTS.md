# RuleIQ Working Rules

Repository files are the recovery source of truth.

1. Start with this file, [continuity](docs/execution/CONTINUITY.md), and its active plan. Inspect Git. Load only linked contracts/decisions relevant to the change; read the roadmap only at stage transitions. After compaction, reload continuity and the active plan.
2. Continuity alone owns current status, blockers, evidence links and exactly one next action. Plans own scope, acceptance and validation. Root alone writes global state. Update at completed batches, blockers, accepted decisions and handoffs; discussion alone needs no update.
3. Reuse approved plans and inspected source until they change; replan only for material conflicts/scope changes. Search before reading; default output to 1,500 tokens, expanding for required complete content. Archive history rather than loading it at startup. Limits: this file 2,000 characters; continuity 3,500; active plan 6,500; combined 12,000. Reorganize oversized summaries without dropping technical requirements.
4. Follow [workflow rules](docs/execution/WORKFLOW.md) for high-risk changes. Finish the entire approved refactoring batch, including workflow edits, before one independent read-only gpt-6-astra/xhigh review. No separate workflow/activation/design/closure reviews. Root fixes findings; recheck affected behavior, broadening only if scope expands. VERIFIED requires PASS. Routine documentation uses root checks.
5. Run relevant checks after changes and the complete required gate before closure. Reuse evidence only while tested files, inputs, configuration and environment remain applicable. Preserve unknown/unverified distinctions; static checks do not prove Pega runtime behavior.
6. At handoff run `python -B scripts/check_project_state.py`. Routine updates: 1-2 sentences. Checks: one success summary or relevant failure diagnostics. Link details without repeating them. Do not commit, push or deploy without authorization.

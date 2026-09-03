# RuleIQ Repository Continuity Rules

Repository files, not model memory, are the source of truth after a chat restart.

1. At session start, read `docs/execution/CONTINUITY.md`, `docs/execution/ROADMAP.md`, the active ExecPlan named in continuity, and the relevant entries in `docs/decisions/DECISIONS.md`.
2. Verify recorded state against Git and the repository before acting; reconcile discrepancies in the continuity artifacts.
3. Follow the active Roadmap stage and maintain exactly one `Exact next action` in continuity and in the active ExecPlan.
4. After every material project-state change, update continuity and any affected roadmap, plan, or decision entry with evidence from the repository.
5. Use the defined evidence classifications and never describe unverified work or tests as verified.
6. Re-read the continuity artifacts after context compaction before continuing work.
7. The root agent is the sole writer of global continuity artifacts. After each high-risk change, it must stop dependent work, launch an independent read-only validation subagent, receive its report, and apply any corrections itself before proceeding.
8. Do not update continuity artifacts for discussion-only turns that make no material project-state change.

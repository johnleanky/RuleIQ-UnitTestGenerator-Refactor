# S7 — Author presence and Standard grouping

Execution state and the next action belong to [continuity](../CONTINUITY.md).

## Scope and accepted decisions

Apply the user-approved Author-instruction-only correction. Distinguish initial/final presence from values and executed-write status; skipped writes preserve state. Only proven final absence permits Not exists. Unknown presence requires existing omissions/gaps and appropriate testability. Retain input-only exclusions, seed conflict repair, nested-path semantics and list safety. Qualify the never-written shortcuts from KP.10/KT.36 in the Author gate without changing KnowledgeAreas. Preserve the existing trace whitelist; remove the conflicting Author request for a candidate gate annotation.

Clarify one Standard ScenarioGroup per frozen scenario in both the early authority paragraph and Section 11. Preserve IDs/order; local scenario order is 1. The broader initial-scenario-locking/compiler correction remains separate.

## Interfaces and preservation

Source revision 1.4, source-reader enforcement, Memory/tool signatures, candidate schemas, Generator, Validator, exports and reference-only Main_Agent.txt remain unchanged. Add no mandatory presence-proof contract. [Pre-edit baseline](../evidence/S7-baseline.json) preserves original Author bytes and hashes of all outside-scope existing files, including closed S6 evidence. Only Author and current continuity/roadmap may change among baseline files; new fixtures, gate, plan and evidence are local deliverables.

## Acceptance and validation

- Policy examples cover known absence/presence, null/empty, unknown state, skipped/executed writes, removal/recreation, seed exclusion, input-only claims and nested paths. Prompt checks reject conflicting old shortcuts.
- A connected synthetic Standard flow preserves S1/S2 as G001/G002 with local order 1. Reuse the S6 gate for unchanged source/candidate compatibility.
- GetCaseData S2 retains structural absence claims only under an explicit mock fresh-harness guarantee for all four output paths. Without it, retain S2 and omit unsupported claims; if none remain, mark NotTestable. Neither variant adds a simulation.
- Run `.venv-s6/Scripts/python.exe -B scripts/validate_s7_author.py`, `python -B scripts/check_project_state.py --self-test`, and `git diff --check`. Reuse applicable historical S5 evidence from the closed S6 batch; its fixed checkout and environment are unchanged.
- Complete the entire batch before one final independent read-only gpt-6-astra/xhigh review. Recheck only corrections and affected behavior unless scope expands.

Policy examples test a reference interpretation, not Pega or model execution. The presence policy remains an Author responsibility; consumers still trust frozen decisions. No Pega verification, deployment, commit or push is included.

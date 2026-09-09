# S6 — Data Page Parameters and Crawler Controls

Execution state and the next action are owned by [continuity](../CONTINUITY.md).

## Scope and decisions

Implement [DEC-033](../../decisions/DEC-033.md) and [source revision 1.4](../../contracts/SCENARIO_GROUP_V1_4.md). Update Data Page guidance, all affected Author/Generator/Validator prompts and exports, revision-aware source checks, both candidate schemas and examples together. The user also approved removing complexity scoring in the same unreleased revision 1.4. Preserve tool signatures, Memory addresses, schema identifiers and candidate fields unrelated to scoring. Follow [current workflow](../WORKFLOW.md); prior activation/design milestone sequences are historical.

The user confirms implicit same-name current-Param binding for declared Data Page inputs in RuleIQ. Unknown export field mappings remain unresolved. Explicit arguments win, then present current values, then evidenced applicable defaults. Null, empty, absent and unknown remain distinct. Resolve each access against preceding executed producers; skipped and unknown execution retain their evidence. Crawl records symbolic bindings; execution freezes concrete maps. Seed external inputs, never values produced by the RUT.

Parameter refinement preserves existing scenarios and changes only their details/testability. The broader initial-scenario locking redesign, Model WHEN field mapping, STRING alias, root-Data-Page assertions and the two separate Validator findings remain outside this batch. Main_Agent.txt stays reference-only. No Pega deployment/runtime verification is included.

## Interfaces

Revision 1.4 adds PARAM mode=default and evidence-backed absent SIM.parameterResolutions for empty effective maps, preserving trace whitelists. Replace COMPLEXITY, in its existing position, with `CRAWL|ruleCrawlerCalls=<N>|dependencyReferencesRequested=<N>|triggeredLimits=<codesOrAbsent>`. Remove SUMMARY.complexityTier, ComplexityTier, ComplexityComputed, weighted scores, thresholds and complexity-derived confidence/testability caps. Keep crawler limits of 120 calls/260 requested references, actual wave/request accounting, closure and terminal-gap rules. Determine confidence/testability from actual evidence and assertion support; removal alone does not promote scenarios. Author emits complete declaration/access/execution/current-state evidence under the linked contract; Generator audits immutable facts and rejects older current-source inputs. Validator remains candidate-only. Preserve historical contracts and fixtures at their fixed baseline rather than migrating immutable records in place.

## Acceptance

1. KnowledgeArea owns binding order, timing, known-empty versus unknown metadata and caller-versus-loader distinction; Thread-only eligibility remains.
2. Author captures symbolic producers without blocking on future values, preserves scenario scope and does not seed RUT-produced inputs.
3. Parser/checker enforces typed values, complete current-state/producer census, default provenance, UNKNOWN gaps and exact SIM/PARAM mapping; reject missing, extra, duplicate or unrelated references.
4. Positive/adversarial fixtures cover explicit, implicit, default, unresolved, overwritten, skipped, unknown and repeated access, null/empty/Boolean/numeric inputs and parameterless pages.
5. Labeled GetCaseData simulation verifies step 1.1 yields GENUT-11007, reads 1.3/1.4 use that pyID, and the false branch has no simulation. Do not claim complete RUT readiness while unrelated KT/STRING defects remain.
6. Connected static flows prove immutable source handoff and schema-valid candidates; historical suites remain passing at the fixed baseline.
7. Both families pass without scoring fields; nested deterministic calls no longer force partial testability, while missing evidence/unsupported assertions still downgrade. Boundary counters, wave consistency, limit failures and rejection of obsolete fields pass.
8. Selected prompt/export parity, unchanged external metadata, bounded instruction traceability and independent required-profile PASS are complete. Coordinate producer/consumer/schema deployment; old immutable candidates remain historical and are not silently rewritten or revalidated against the changed schema. Retire scoring-only KnowledgeArea instructions while preserving runtime context guidance and marker traceability.

## Validation

Implement and run `python -B scripts/validate_s6_parameters.py`; its `--historical` option must run unchanged S5 checks in an isolated fixed-baseline checkout. Run `git diff --check`. Those S6 scripts are planned deliverables, not existing verified checks. Baseline: 13b44c7f59c250d3a54fb11d4dfb6ecbb5db24a8. Preserve deterministic line endings in isolated historical checkouts.

## Evidence and risks

[Independent design review](../evidence/S6-design-review.md) records the completed design gate and its limits. That review covers the original Data Page design; the user-approved scoring removal expands implementation scope and requires the combined implementation review. Simulation retains S1 (step 1 TRUE) and S2 (FALSE); current compiler FALSE-edge exclusion, reduction and ID reassignment conflicts remain tracked under the separate scenario-locking correction. Static snapshots prove consistency, not arbitrary RUT evaluation or Pega metadata extraction. Review the cohesive implementation batch before dependent work and closure.

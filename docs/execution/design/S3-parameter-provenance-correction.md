# S3 Formal Parameter Provenance Correction

- **Stage:** S3 prerequisite within design freeze
- **Status:** `VERIFIED`; focused independent PASS and root reconciliation complete
- **Decision:** DEC-026
- **Baseline:** `8509a508ee586136b4a06caa86ee50a51a391b0e`
- **Scope:** one cohesive Scenario Author/ScenarioGroup handoff correction; no Generator or Validator product artifact

## Evidence and Defect

The original canonical Main prompt at `b9dd565` lines 1554–1565 requires matching a parameter's exact name to its original RuleJSON formal declaration and selecting serialization by the declared Pega type. It forbids inferring that type from the value. The S2 revision-1 PARAM grammar retained resolution mode and valueType but had no formal declaration field or required structured provenance. INPUT.mode is property/input metadata; PARAM.dependency=RUT also occurs for primary When input bindings, so neither proves formal parameter identity.

The missing distinction is observable: String `InputPage` needs a quoted Pega string literal, while PAGE `InputPage` needs a page reference. A typed fractional number is valid for Decimal and invalid for Integer. Boolean/TrueFalse must not be inferred from a string that happens to contain `false`.

## Correction and Boundaries

[ScenarioGroup revision 1.1](../../contracts/SCENARIO_GROUP_V1.md) adds PARAM.formalType and PARAM.formalEvidence. The physical `Param.` carrier determines whether a record represents an actual RUT argument. Exact-name source evidence determines its type. Ordinary When property bindings and Data Page/dependency parameters keep both new fields absent.

The evidence is a bounded, typed snapshot of the original formal declaration with its array index. Failed unique-name lookup uses explicit array-level evidence and a null type. Missing, unknown, unsupported, wrongly typed, or unrepresentable parameter projections retain the semantic source and produce a named projection GAP; they cannot yield a runnable Scenario by dropping just its parameter. Full Generator failure-report/index handling remains part of the later S3 contract design.

Revision 1.1 rejects old revision 1 and unknown revisions. Scenario Author rematerializes from original RuleJSON and writes new immutable records; consumers do not relabel or upgrade old Payloads, infer metadata, change Memory Type, retry writes, or mutate stored sources. Contract filenames continue to identify the v1 family. There is no deployed-runtime compatibility claim.

The static parameter-value oracle implements only the source decision table for test evidence. It is not a Pega agent, a complete UnitTestRules projector, or an alternative schema validator. Future field assembly must obey the existing STANDARD schema: MethodParam.pyParametersParamType permits PAGE only; scalar type provenance does not authorize emitting String/Integer/Decimal/Boolean there. MultInpComb has a different MethodParam type enum and carries per-combination scalar values in Decision input cells; its complete mapping remains part of S3 design freeze.

The existing SUMMARY derivation is tightened so any GAP prevents Closed, including a projection gap when every dependency row is NOT_APPLICABLE. This restores the existing no-gap closure rule; it does not add dependency calls or change semantic coverage.

## Source-to-Destination Trace

| Source | Preserved obligation | Correction destination | Regression |
|---|---|---|---|
| IPM-AUTH-035; original Main 541–553 | Preserve original parameter identity, resolution, value, and evidence without guessing. | Main §5.2 metadata capture; PARAM formalType/formalEvidence and indexed EVIDENCE snapshot. | Complete-array unique exact-name selection and bounded snapshot equality, exact name/binding, evidence link/source checks. |
| IPM-AUTH-072; original Main 1517–1530 | Versioned complete immutable snapshot with exact grammar. | SG.version=1.1; old-arity/version rejection; new immutable writes only. | Both old version and old PARAM arity fail; five existing fixture semantics are preserved. |
| IPM-AUTH-078; original Main 1554–1565 | Formal Pega type governs projection; missing/unknown type is not guessed. | Metadata capture remains Author-owned; parameter formatting stays Generator-owned. | 22 exact formatting/type cases, including String/PAGE, Integer/Decimal, empty and escaped strings, Boolean/TrueFalse, unsupported types. |
| IPM-AUTH-105; original Main 2202–2203 | Complete source snapshots precede Generator invocation. | Required provenance and explicit projection-gap materialization in the handoff. | Standard and When ledgers, 10 unavailable-type/gap cases, 26 malformed-ledger mutations, 14 raw-source cases, 16 source mutations, and eight persisted-payload corruptions. |
| IPM-AUTH-088; original Main 1832–1865 | Terminal gaps and closure state agree; no false Closed state. | SUMMARY derivation includes projection gaps even without external dependencies. | When source with NOT_APPLICABLE dependency plus type gap reports Blocked. |

The four directly extended rows 035/072/078/105 cite DEC-026 in the existing S2 slice and executable row catalog. Row 088 retains its existing no-gap closure requirement. Historical S2 closure remains valid for its original revision; current correction verification is separate.

## Reproducible Checks

- `python3 -B scripts/validate_s2_design.py` checks all 106 existing rows and the five updated source fixtures, exact prompt/contract synchronization, the revision-1.1 full-content digest, and the previous semantic/orchestration/encoding guards.
- That checker removes only the three bounded DEC-026 text additions and the exact PARAM/version grammar edits in memory, then requires the original S2 canonical digest `6F059B641B9CF8B627E6879ED5B7A8FAEE78A616E71E2DD305AF8C051ACD215F`. This proves all other prompt instructions remain byte-identical after LF canonicalization.
- `python3 -B scripts/validate_s3_parameter_provenance.py` checks the new standard and When ledgers, synthetic original parameter arrays, 22 projection cases, 10 explicit unavailable-type cases, 26 targeted ledger mutations, 14 raw-source cases, 16 source mutations, and eight raw-payload corruptions. Raw persisted ledgers are validated before parsing; complete-array unique-name checks cover duplicate names, absent names/types, non-string types, exact-case selection, and bounded snapshots from declarations with extra fields. Each negative test must fail for its intended provenance/contract reason.
- `git diff --check` and named-file diffs verify scope. All 14 other product `.txt` files, S1 caller contracts, both schema/example families, and reference-only `Main_Agent.txt` must match baseline.

These are repository-static checks. Prompt execution, Pega import, external Memory, and runtime schema-validation behavior remain unverified.

## Review Gate

Stop dependent S3 design and Generator product work until an independent read-only `gpt-6-astra` / `xhigh` reviewer validates the complete correction against the baseline, original clauses, DEC-026, fixture semantics, and the commands above. Root alone reconciles findings and makes corrections; high-risk corrections require focused follow-up.

## First Review and Corrections

- `FAILED` — independent `/root/review_s3_formal_parameter_handoff` (`gpt-6-astra` / `xhigh`) found three P2 static-validation gaps: mislabeled formal INPUT carriers, normalized raw payloads, and unchecked duplicate source declarations. Its preservation and scope checks passed.
- `IMPLEMENTED_NOT_VERIFIED` — root added strict Param namespace/role/group guards in the synchronized prompt/contract and checker, raw persisted-file validation with direct corrupt-file probes, and complete-array source selection with explicit raw-source fixtures. Both suites and whitespace checks pass; focused independent follow-up remains required.
- `VERIFIED` — focused independent follow-up from the same `gpt-6-astra` / `xhigh` reviewer returned PASS with no remaining findings. It reproduced 15 original bypass rejections and both full suites. Root reconciled the report, preservation/scope, links, whitespace, and cache hygiene; the correction gate is closed and dependent S3 design may resume. The first FAIL is retained above as historical evidence.

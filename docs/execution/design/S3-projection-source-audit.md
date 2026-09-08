# S3 Projection Source Audit

- **Stage:** S3 design freeze
- **Status:** `PARTIAL` — historical source observations are verified; DEC-027 implements the consolidated source correction with focused independent PASS, and full Generator design is not yet frozen
- **Baseline:** Git HEAD `8509a508ee586136b4a06caa86ee50a51a391b0e` plus the independently verified DEC-026 working correction
- **Scope:** Read-only source sufficiency findings; no new wire revision, field default, rejection policy, or agent implementation is defined here

## Sources and Authority

The original Main prompt is `b9dd565:Main_Agent_Prompt.txt`. Both candidate schema families remain byte-identical to HEAD: `rule-test-unit-case_JsonSchema.txt` and `rule-test-unit-case_multInpComb-JsonSchema.txt`. Their examples are illustrative and cannot establish a runtime value for a different case.

[ScenarioGroup revision 1.1](../../contracts/SCENARIO_GROUP_V1.md) supplies the immutable semantic input. [The DEC-026 correction](S3-parameter-provenance-correction.md) has independent PASS and closes formal-parameter type provenance only. Generator cannot query GetCaseData or RuleCrawler; [S1](../../contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md) fixes its input to CaseID, immutable RUTType, and ordered ScenarioGroup UUIDs.

## Current Disposition

The user confirmed on 2026-09-07 that Ruleset/Version selection is already implemented in Pega and is outside this task. Do not add the proposed TargetRuleSet/TargetRuleSetVersion fields. DEC-027 revision 1.2 supplies case-key provenance, fixed/source-evidenced single-page mode, ordered actions, per-ASSERT property/APB bindings and optional context, individual checklist facts, and final reasoning/closure traces. Its corrected implementation and tests passed focused independent review and root reconciliation. The table below is retained as the discovery record; it does not override this disposition. Complete candidate mapping and operational Ruleset/Version configuration are distinct concerns.

## Historical Metadata and Action Source Inventory

| Candidate obligation | Existing source evidence | Design-freeze disposition |
|---|---|---|
| RuleCode.pyRuleSet | SG.ruleset exists. | Specify its target-ruleset meaning and exact projection; do not replace it with an example value. |
| Required RuleCode.pyRuleSetVersion | Both schemas require a formatted version and describe selection of the active open UT ruleset version. The SG header has no version field or prescribed version evidence record. | Resolve the authoritative source and handoff before accepting a projection. Neither an example's `01-01-01` nor the RUT's own version establishes the target version. |
| Required pyRuleUnderTestInsName | Both schemas prescribe uppercase Apply-To and rule name from the case's TestedRuleKey. SG has rutClass/rutName, but carries no TestedRuleKey or required evidence proving their equality to its components. | Define a provenance-preserving identity mapping and mismatch handling; do not claim that constructing a string from SG proves case-key correspondence. |
| Required pyIsSinglePageImplementation | Both schemas require a string. STANDARD specifies `false` for Rule-Obj-Model in its description; MultInpComb enforces `const=false` as a string for Rule-Obj-When. SG.rutType preserves the original type. No source field or rule is prescribed for all remaining supported types. | Retain the Model and When rules; determine the source or accepted behavior for other types before freezing the complete mapping. Do not generalize an illustrative example. |
| Runtime RUT parameter values | Revision 1.1 binds each physical Param input to its unique original formal declaration evidence and typed value. | Verified prerequisite: use the DEC-026 type table; STANDARD scalar MethodParam records omit pyParametersParamType because that schema allows only PAGE in the field. MultInpComb allows additional formal type labels and carries per-combination scalar values in input cells; specify its distinct mapping explicitly. Unavailable projection requires the future scoped Generator report. |
| Setup page values and P&C | ROOT and INPUT/SETUP records carry exact pages, classes, paths, and typed values; DTA_BEFORE binds invocation-page setup. | Define the lossless path-to-seed projection and conflict checks; distinguish initialized empty cells from absent values. |
| Required pre/post execution actions | Original Main line 1572 retains pySetup/pyCleanup for required actions; both schemas define SetupAction. SETUP grammar carries only property/page data with roles SETUP, DTA_BEFORE, PAGE_AND_CLASS. Generic evidence prose does not define ordered action kind/name/target/parameters or their absence. | Audit whether action semantics require a structured handoff extension. Do not equate page seeding with executing an action or silently omit a required action. |
| Optional evidenced Pega assertion context | Original Main 1475–1493 requires retaining applicable context and compact Page forms. ASSERT supplies core target/page/class/mode; other evidence records are available but have no universal optional-context projection mapping. | Audit each source-required optional field and define its immutable source or explicit non-applicability. Schema optionality alone is not proof that a recorded runtime field may be dropped. |

At discovery, these findings did not prescribe a new default or require a new external interface. The active plan already permits a separately reviewed correction if a blocking handoff defect is confirmed. DEC-027 now consolidates this source audit; the completed DEC-026 correction remains verified for its bounded scope.

## Verification and Remaining Work

Root parsed both schemas using UTF-8 BOM support and confirmed that version, instance name, and single-page implementation are required in both families; the STANDARD MethodParam type enum allows only PAGE, while MultInpComb allows Text/Integer/Decimal/Double/TrueFalse/Date/DateTime/PAGE. Original Main line 1572 and both SetupAction definitions confirm the action obligation. The current ScenarioGroup grammar and Author allowlist were inspected for the corresponding source carriers. No external runtime or tool behavior is inferred.

The full S3 package now contains the 150-row disposition slice, Generator/report contract, source-to-field mapping, source/rejection/index rules, candidate-version orchestration, export metadata evidence, and executable positive/adversarial fixtures; independent design review remains pending. DEC-028 records the user-owned Pega target-template carrier interpretation without selecting or implementing Ruleset/Version configuration. This audit is supporting evidence for that package, not its acceptance or an implementation result.

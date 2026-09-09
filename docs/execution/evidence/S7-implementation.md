# S7 Author correction evidence

- Authorization: user-approved [instruction-only plan](../plans/S7-presence-grouping.md). [Baseline](S7-baseline.json) captures HEAD/Git status, original Author bytes and 169 protected files. Closed S6 evidence is preserved.
- Instruction traceability: Main sections 1.3/11 clarify per-scenario Standard groups; 5.3 WR projection distinguishes execution from presence; 5.3b STEP 4 separates seed eligibility; 6.0-PRE replaces unconditional absence, qualifies KP.10/KT.36 shortcuts, preserves eligibility/list safety and the existing trace whitelist. The gate marker is retained internally.
- Validation boundary: [policy fixtures](../../../fixtures/s7/presence-policy.json) are expected Author decisions exercised by a test-only reference interpreter. They do not demonstrate Pega semantics or guaranteed model behavior. No presence-proof consumer contract was added.
- Handoff boundary: [gate](../../../scripts/validate_s7_author.py) uses existing full source parsing, Memory doubles, projection and candidate validation to verify two synthetic Standard groups retain S1/S2 IDs and local order 1. These witnesses are not full GetCaseData scenarios. The gate also runs the current S6 gate and verifies outside-scope hashes.
- Root checks: S7 gate PASS (23 policy examples, 2 S2 variants, connected Standard handoff, all 74 S6 check groups, 169 preserved files); management self-test PASS (23 negatives; 6,971 startup characters); whitespace PASS. Applicable fixed-baseline historical S5 PASS is reused from unchanged S6 evidence. Actual token telemetry unavailable.

## GetCaseData simulation refinement

S2 remains the step-1 FALSE scenario, CaseKey `OTHER-WORK CASE-20001`, with no Data Page simulation. With the explicitly labeled fresh-harness absence guarantee covering Param.pyID, .pyID, .TestedRuleKey and .RuleJSON, their Structural Not exists claims remain simulation expectations. Without that evidence, all four presence claims are unresolved and omitted under unresolvable_runtime_input; S2 remains identified and is NotTestable if no other meaningful assertion remains. Its ID, target and order are unchanged. No Memory write occurred.

The original scenario-lock override and separate Model WHEN field, STRING alias, direct Data Page assertion and Validator corrections remain outside this batch. Assertion-only refinement does not remove a scenario or prove Pega runtime readiness.

# ScenarioGroup v1 Contract — Revision 1.3

- **Owner:** Scenario Author
- **Consumers:** UnitTestGenerator and, through generated trace projection, Validator
- **Transport:** `WriteMemory(CaseID, Type="ScenarioGroup", Payload)`
- **Contract status:** revision 1.3 is `VERIFIED` after DEC-029/full S3 design focused independent PASS and root reconciliation; earlier revisions retain historical verification
- **Runtime status:** repository-static only; Pega tool implementation and runtime proof are external under DEC-019

## Purpose and Boundary

Revision 1.1 adds explicit formal RUT parameter provenance under DEC-026. Revision 1.1 originally added formal provenance; revision 1.3 below is now the required producer/consumer revision and rejects every older or unknown revision before projection. This is a required-field grammar change, not an in-place Memory upgrade: Scenario Author must rematerialize from the original RuleJSON and write new immutable ScenarioGroup records. Never relabel an old payload or infer missing metadata. The v1 family filename and Memory Type `ScenarioGroup` remain unchanged.

A ScenarioGroup payload is the complete, immutable semantic snapshot for exactly one physical unit-test group. It is not candidate JSON, does not contain `UnitTestRules` or `RuleCode`, and cannot ask UnitTestGenerator to crawl, infer expected values, alter grouping, or make new ASSERT/SIM/OMIT decisions. UnitTestGenerator may only validate this contract and project its frozen facts.

Scenario Author writes one payload for each final physical group, in stable group order. It calls `WriteMemory` once per group with the exact CaseID, Type `ScenarioGroup`, and payload bytes. It preserves each returned UUID opaquely. Only after every write succeeds does it call UnitTestGenerator exactly once with the exact CaseID, immutable original RUTType, and ordered UUID array. A failed or malformed write is terminal: no retry, no partial Generator call, and no deletion or overwrite of earlier immutable records.

The WriteMemory result envelope is the exact S1 contract: fields are exactly `Success` (boolean), `UUID` (string), `ErrorCode` (string), and `ErrorMessage` (string). `Success=true` requires a non-empty opaque UUID and empty error fields. `Success=false` requires an empty UUID, non-empty ErrorMessage, and ErrorCode `INVALID_INPUT`, `UNSUPPORTED_TYPE`, or `WRITE_FAILED`. Missing, additional, wrongly cased, wrongly typed, or contradictory fields are malformed and follow the same terminal no-retry/no-handoff path. UUID collection begins only after this complete envelope check.

### Revision 1.2 source profile

DEC-027 extends revision 1.1 with exactly one PROFILE per Scenario. Revision 1.2 introduced this common profile; revision 1.3 below governs current producers and consumers. Generator rejects older or unknown revisions and requires new immutable rematerialization from the original source. The unchanged legacy record definitions below retain their arity, including END: PROFILE count is derived from scenarioCount and its exact one-per-Scenario census. In the per-Scenario record sequence PROFILE is first, immediately before PARAM (or the first present legacy body tag); its ID is F001 and order is 1. Every other legacy count excludes PROFILE. The five S2 fixtures remain historical revision-1.1 regressions; historical revision-1.2 examples are under fixtures/s3/profiled/.

`PROFILE|scenario=<ID>|id=F001|order=1|data=<canonicalTypedJSON>|evidence=<sortedEvidenceIDs>`

PROFILE.data has exactly `caseKey`, `singlePage`, `scenarioType`, `actions`, `bindings`, `checklist`, `reasoningTrace`, and `dependencyClosureTrace`. It contains final source facts, not candidate JSON or a second scenario/coverage ledger. Case identity and runtime metadata are the same across every Scenario in a group.

- `caseKey` is exact GetCaseData.TestedRuleKey. Its first three whitespace-separated components must equal uppercase SG.rutType, SG.rutClass, and SG.rutName. Before freezing, Author verifies this correspondence against the original RuleJSON identity; missing or conflicting identity terminates materialization rather than inventing a key. A linked EVIDENCE with kind=RUT, source=GetCaseData/TestedRuleKey and canonical fact `{"TestedRuleKey":<exactKey>}` preserves the original value.
- `singlePage` is the string `false` for original Rule-Obj-Model and Rule-Obj-When, as prescribed by the respective schema contracts. For another type, copy an evidenced original RuleJSON.pyIsSinglePageImplementation string `true` or `false`, using linked RUT evidence at source RuleJSON/pyIsSinglePageImplementation with the one-field canonical snapshot. If unavailable, store JSON null and GAP code RUT_EXECUTION_MODE_UNAVAILABLE; the Scenario cannot be Testable and cannot be projected as runnable. Do not infer this flag from rule names or examples of another type.
- `scenarioType` is the frozen semantic category Baseline or Edge. Author chooses it during Scenario formation from the final purpose, not from schema formatting; Generator copies it.
- `actions` is the complete ordered array of required setup actions followed by required cleanup actions. An empty array is an audited absence, not permission for Generator to invent actions. Each object has exactly `phase` (SETUP or CLEANUP), `type` (ApplyDataTransform, RunActivity, LoadDataPage, LoadObject, CreateDataObject, CreateWorkObject), exact nonempty `name`, `page` (a ROOT page or JSON null), `parameters`, and nonempty same-Scenario `evidence` ID array. Parameters preserve order and unique exact names. Each has exactly `name`, `formalType`, `valueType`, `value`, and nonempty `evidence` ID array. Its formal type comes from the referenced action's declaration, its value from frozen execution, and the DEC-026 value table must support its projection. Unknown actions/parameters must be resolved during witness formation or cause explicit terminal failure; they cannot be silently dropped. A mocked Data Page never becomes a LoadDataPage action. Distinct shared When actions are not grounds for downstream regrouping.
- `bindings` is one ordered object for each non-cell ASSERT, in ASSERT order; DecisionInput/DecisionResult assertions have no binding. A non-cell ASSERT in a WHEN source is retained with its binding for explicit projection-scope handling, never silently discarded. Each object has exactly `assertion`, `structure`, `scalarType`, `stepPage`, `stepClass`, `fullPath`, `parentMode`, `context`, and a nonempty same-Scenario `evidence` ID array. Capture property definitions and final APB/runtime context before freezing. `structure` is Value, Page, ValueList, PageList, ValueGroup, PageGroup, or NotApplicable. `scalarType` is Text, String, Identifier, Password, TextEncrypted, Integer, Double, Decimal, Date, DateTime, TimeOfDay, TrueFalse, or NotApplicable. `stepPage` is an evidenced ROOT pagesAndClasses root and `stepClass` is its class. `fullPath` equals the immutable Param/full ASSERT target, or ASSERT.page plus a leading-dot target. Non-Param fullPath begins with stepPage plus a dot; never guess a second root from serialized JSON. A scalar Property cannot target a Page/PageList/PageGroup itself. For a scalar Property, parentMode is ValueList/ValueGroup only for that declared indexed/keyed value structure and otherwise JSON null; Param assertions keep Text mode and no parentMode. Other parentMode values, when applicable to a non-Property binding, are PageList or PageGroup. Scalar property modes agree with the resolved scalarType.
- `context` preserves evidenced optional assertion-block fields by their exact Pega names: pyCardApplyToClass, pyPropertyApplyToClass, pyStepPageNameActual, pyStepPageMethodName, pyListFilter, pyNumberOfAppearances, and pyComparator. Values are nonempty strings. Filters apply only to List/ResultCount; List pyNumberOfAppearances is InAllInstances for all-items checks or InAnyInstance for the preserved proven-payload/unknown-index fallback; retain the Author's evidenced choice. A Page block comparator, if present, equals its ASSERT comparator. Core target/page/class/expected-value fields cannot be overridden through this object. Absence means no applicable optional source field survived the semantic audit, not that Generator may discard an evidenced field.
- `checklist` contains exactly the 17 Author-owned boolean facts: CandidateAssertionsEnumerated, DependencyResolutionCompleted, RuleCrawlerLimitsApplied, RUFTransitiveDiscoveryCompleted, ParametersResolved, BranchesEvaluated, PropertyTracesCompleted, OmissionsResolved, ComplexityComputed, SimulationNeedsResolved, SimulationDepthChecked, ListAssertionsChecked, SymbolicIndexesResolved, ContextSwitchesResolved, UnsupportedAssertionsExcluded, NoSpeculation, NoInternalLedgerLeak. Record actual gate results; never fill them from a blanket success template. RuleCodeConsistentWithLedger and SchemaSelfCheckPassed remain Generator-owned and are excluded. A false semantic gate must be represented by a GAP and appropriate confidence/testability limits.
- `reasoningTrace` and `dependencyClosureTrace` are final nonempty compact factual strings. Author freezes the actual wave STATE/PLAN/DELTA proof, relevant DTM/DTE/DTA projections, assertion permission/omission reasons, and seed-to-assertion evidence required by original Main 1832–1865. No invented RuleCrawler wave or fetched rule is allowed; no-crawl runs say so. Generator preserves these strings and appends only its own bounded projection facts if needed; it never synthesizes missing crawl history.

PROFILE.evidence resolves in the same Scenario and includes the case-key proof and one GATE EVIDENCE at source SCENARIO_SNAPSHOT/PROFILE whose canonical fact equals PROFILE.data exactly. This records the final audited source-profile census. All nested evidence references resolve to actual acquisition/execution evidence; the census is not a substitute for that source evidence. Freeze the profile together with INPUT/SETUP/ASSERT/SIM/OMIT and re-audit it after any semantic change. No existing coverage, expected value, simulation, or stable Scenario ID may change merely to make the profile serializable.

Nested acquisition snapshots are mandatory and cannot cite the PROFILE census as their provenance. Keep exact original acquisition values before building PROFILE; do not create a snapshot by reverse-copying a completed profile. Same-Scenario EVIDENCE facts use canonical JSON and the following sources:

- For each binding, DEPENDENCY source `PROPERTY_DEFINITION/<assertionID>` captures `path`, `pyPropertyMode`, and `pyStringType` from the resolved property definition and its lookup path. They equal fullPath, structure, and scalarType. EXECUTION source `ASSERTION_CONTEXT/<assertionID>` captures exactly stepPage, stepClass, fullPath, parentMode, context, producerIndex (Known, Unknown, NotApplicable), and payloadProven (boolean) from the audited APB/producer state. All five common fields equal the binding. Both IDs occur in binding.evidence. A List with unknown producer index requires proven payload and InAnyInstance; its uncertain index must never be turned into an all-items or positional assertion. This preserves IPM-AUTH-046.
- EXECUTION source `EXECUTION_ACTIONS` is the complete ordered array of action identities, each with exactly phase, type, name, and page, captured during witness execution. PROFILE.evidence links it even when empty; every action.evidence links the same snapshot. For each action argument, DEPENDENCY source `ActionRule/<type>/<name>/pyParameters` captures the complete original declaration array. Select exactly one declaration with the exact pyParametersParamName and matching pyParametersParamType; duplicate/missing names fail. EXECUTION source `ACTION_ARGUMENTS/<zero-based-action-index>` captures the complete ordered resolved argument array with name, valueType, and value. PROFILE.evidence links every ACTION_ARGUMENTS snapshot, including a genuinely empty array. Validate that complete ordered array once per action before iterating its parameters; removing all parameters cannot bypass the source census. Each parameter.evidence additionally links both snapshots. Nested value is a decoded ledger carrier: string for every non-absent valueType, JSON null only for absent. It still obeys the DEC-026 typed-value/formal-type table; a JSON number, boolean, array, or object cannot masquerade as a string literal.
- EXECUTION source `EXECUTION_AUDIT` captures exactly waves and seeds from the actual dependency/witness run and is linked by PROFILE.evidence. waves is ordered and has exactly MaxDependencyWaveReached entries, no more than the group RuleCrawler call count. Each entry is `{wave,state,plan,delta}`: wave is the contiguous one-based actual wave; state has nonnegative integer open/ready/ctx/unscanned/gaps; plan has OUT/BLK/ACT arrays of exact recorded dependency identities and CHK=PASS or FIX; delta has returned/new/ready/closed identity arrays and next=CRAWL, AUTHOR, or TERMINAL_BLOCKED. No duplicate or unknown identity is allowed. returned means fetched RuleJSON, is a subset of OUT, and cannot claim a MISSING/KEYONLY/LIMIT dependency; closed requires a CLOSED dependency. Final ready count equals QueuedDependencyCount and next agrees with Closed/Blocked. Capture terminal missing outcomes in the actual DEP state/proof, never fabricate returned content.
- seeds is an array of `{source,assertion,expression,seedPath,assertionPath,evidence}`. source resolves to a SETUP/SIM ID, assertion resolves to ASSERT, expression preserves the audited source expression, assertionPath equals the immutable ASSERT target, and seedPath is the actual `pySetupPages.<page><path>` or `pyPageDetails.<payload-path>`. Evidence resolves to the original SEED/EXECUTION acquisition, excluding the census and EXECUTION_AUDIT itself. Include every seed that supports an exact assertion; SETUP-to-assertion same-path pairs require proof. An unused seed does not justify inventing an assertion or a seed-to-output relationship.

Freeze the two trace strings by rendering these acquisition facts and existing rows, without additional inferred history. DependencyClosureTrace contains `STATE W<n>`, `PLAN W<n>`, `DELTA W<n>` with every captured field and important `D <identity>: state=<state>; proof=<proof>` rows; zero waves explicitly says `No RuleCrawler waves occurred.` ReasoningTrace contains the same wave facts with RCSTATE/RCPLAN labels, compact final DTM/DTE/DTA/DTC/DTRA and ASSERT/OMIT row projections, and each `source expression → final seed path → asserts assertion path` proof. Use the deterministic source rendering in scripts/sg_profile.py for repository fixtures; its exact equality check rejects fabricated, changed, or missing facts. Generator copies these final strings; source acquisition and final trace completion remain Author-owned. The fixture acquisition catalog stores these separate snapshots, not a second copy of PROFILE, and checks their exact preservation.

Target Ruleset/Version selection is already implemented in Pega and remains outside this refactor per the user clarification on 2026-09-07. Do not add TargetRuleSet/TargetRuleSetVersion inputs, select an active target version here, or implement Pega persistence configuration. The source profile adds no such fields. Generator's schema-required metadata carrier handling is specified in its own structural projection contract; it is not a deployment decision.

### Revision 1.3 projection provenance

DEC-029 requires producers to emit `SG.version=1.3` and Generator to reject every older/unknown revision. Never infer or retrofit missing facts in old Memory records; Author rematerializes new immutable sources. Revision-1.2 fixtures under fixtures/s3/profiled/ remain historical; current synthetic Author fixtures are under fixtures/s3/current/. The common PROFILE and legacy record arities remain unchanged.

For each non-cell ASSERT, binding.evidence additionally links exactly one same-Scenario EXECUTION snapshot with source `ASSERTION_VALUE/<assertionID>`. Its canonical fact has exactly `valueType` (string, boolean, number, null, empty, json, absent) and `value` equal to the decoded ASSERT.value carrier. Capture this expected-value type from the final semantic decision before freezing; property mode is not expected-value type. Non-absent carriers are strings; absent uses JSON null. Empty uses `<EMPTY>`; typed null uses `null`; strings such as `null`, `<EMPTY>` or `["Ada","Grace"]` remain literal text when explicitly typed string. Boolean and finite JSON number carriers retain exact values and decimal precision. A json carrier preserves its actual JSON type, array members and order. An array-valued Is In/Is Not In decision must remain an array, never guessed from text or stringified. Comparators without an expected value require absent; ResultCount requires a nonnegative integer number carrier and projects count text only at the downstream block. When DecisionInput/DecisionResult cells retain their existing string/empty contract and need no non-cell binding.

SIM.setupPages is the complete ordered census of actual simulation pages, including the payload carrier; it is never a supplemental list. Every SIM links exactly one same-Scenario EXECUTION snapshot `SIMULATION_BINDING/<simulationID>` with canonical fact `{"itemPath":<exactCollectionPathOrNull>,"payloadPage":<exactPageName>}`. For shape=list, itemPath is the exact evidenced dot-prefixed path from the frozen payload root to its item array; select only that array when validating itemClass. Preserve unrelated arrays and nested fields, which cannot prove the selected collection's class. For shape=page, itemPath is JSON null. This name must identify exactly one page in that nonempty census. Generator places the frozen payload only on this page, merges the explicitly typed page-detail seeds without conflicting overwrites, and emits exactly the full census. Do not prepend a DP-named page or choose PrimaryPage by convention. Preserve the evidenced list wrapper class, domain collection names (including Items or pxResults), item classes and original navigation depth; never invent or replace a wrapper. Missing binding is malformed source; conflicting payload/seed or unsupported wrapper is an explicit unprojectable source scope.

For a simulated WHEN group, each canonical simulationGroupKey.simulations entry has the previous complete fields plus `payloadPage` and `itemPath`, equal to its SIMULATION_BINDING snapshot. All Scenarios in the physical group must match this binding and the full setup-page census as well as every previous simulation-key fact. This explicit revision changes the grouping key; it never authorizes Generator to regroup old records. NO_SIMULATION and STANDARD absent-key rules remain unchanged.


## Encoding

The payload is UTF-8 text without a BOM. Records are separated by raw LF (`U+000A`), and a valid payload ends in one LF. Raw CR and every raw control character inside a record, including horizontal tab, are forbidden. The first record is `SG`; the last is `END`.

Every record has the form `TAG|key=value|key=value`. Field order and arity are normative. Split a record only on unescaped `|`, then split each field on its first unescaped `=`. Tags and keys are ASCII and are never escaped.

Before writing a field value, encode characters in this order:

1. `\` as `\\`;
2. `|` as `\|`;
3. CR as `\r`;
4. LF as `\n`;
5. horizontal tab as `\t`;
6. a value that is exactly `-` as `\-`;
7. an empty string as the exact token `\0`.

The exact unescaped token `-` means absent only where the row definition permits absence. Decode only `\\`, `\|`, `\r`, `\n`, `\t`, `\-`, and `\0`; reject every unknown or dangling escape. Encoding and decoding must be lossless, including delimiter, newline, tab, hyphen, and backslash content. Memory treats the entire payload as opaque and must not perform this decoding.

IDs match `[A-Za-z0-9._:-]+`. Numeric `order` fields are one-based and contiguous within their declared scope. Comma-separated ID sets are sorted and contain no whitespace; `-` is the absent set. Boolean values are lowercase `true` or `false`.

ID assignment is deterministic and freeze-stable. TARGET and SCENARIO IDs are the exact final compiler `T` and `S` IDs. Group IDs are `G001`, `G002`, and so on after stable physical-group ordering. Other record IDs use the tag prefix plus a zero-padded three-digit occurrence number after the record's normative sort inside one Scenario (`F` PROFILE, `C` COLUMN, `K` PARAM, `I` INPUT, `U` SETUP, `R` RX, `D` DEP, `B` BRANCH, `P` PRODUCER, `Y` PROPERTY, `Q` DT family, `Z` DTC, `M` SIM, `A` ASSERT, `O` OMIT, `E` EVIDENCE, `X` GAP, `H` SUMMARY, `N` NARRATIVE). Identical frozen semantics rematerialize identical IDs. A semantic or grouping change returns to WITNESSES, rebuilds the complete snapshot, and reassigns group/local order atomically; consumers never patch IDs in place.

## Required Record Order

Records are sorted by this sequence:

1. one `SG` and one `ROOT`;
2. all `TARGET` records in original-RUT inventory order;
3. zero `COLUMN` records for STANDARD, or one or more ordered `COLUMN` records for WHEN;
4. one `COMPLEXITY` record;
5. all `SCENARIO` records by scenario order;
6. for each scenario, its `PROFILE`, `PARAM`, `INPUT`, `SETUP`, `RX`, `DEP`, `BRANCH`, `PRODUCER`, `PROPERTY`, `DTM`, `DTE`, `DTA`, `DTC`, `DTRA`, `SIM`, `ASSERT`, `OMIT`, `EVIDENCE`, `GAP`, `SUMMARY`, and `NARRATIVE` records in that tag order and then record order;
7. one `END`.

No unknown record, field, or duplicate `(scenario,id)` is allowed. All references resolve inside the same payload. The payload is a complete replacement snapshot; no consumer may combine it with an older ScenarioGroup or a private scenario ledger.

## Record Grammar

The following forms are exact. A field containing `-` is nullable only when its definition below says so.

### Group and Scenario

`SG|version=1.3|caseId=<CaseID>|rutType=<originalRUTType>|rutClass=<class>|rutName=<name>|ruleset=<ruleset>|groupId=<ID>|groupOrder=<N>|kind=<STANDARD|WHEN>|scenarioCount=<N>|simulationGroupKey=<canonicalKeyOrAbsent>`

- `caseId` is exactly `GetCaseData.pyID`; it is not synthesized.
- `rutType` is the immutable original RUT type.
- `kind=STANDARD` requires `rutType != Rule-Obj-When`, `scenarioCount=1`, and absent `simulationGroupKey`.
- `kind=WHEN` requires `rutType=Rule-Obj-When`, one or more scenarios, and exactly one key. A no-simulation group uses the literal `NO_SIMULATION`. Otherwise the key is canonical minified typed JSON with exact root shape `{"simulations":[<entry>...]}`. Object keys are recursively sorted and array order is preserved.
- Across a handoff, `groupOrder` is contiguous and UUID order equals group order.

Each non-empty `simulations` entry has exactly these keys and no others: `itemClass`, `params`, `payload`, `pyClassName`, `pyMockingSupportedRuleTypes`, `pyRuleNameToBeMocked`, `pySimulationMethod`, `pxReferredFromClass`, `setupPages`, `shape`, `sig`, and `target`. Nullable `itemClass` and `pxReferredFromClass` use JSON null. `params` is the canonical typed parameter object and `payload` is the complete typed mock result. `setupPages` is an ordered array of objects containing exactly `pyPageDetails` and `pySetupPageName`; `pyPageDetails` is an ordered array of objects containing exactly `path`, `value`, and `valueType`. The key therefore distinguishes every source-required runtime field, class, shape, method, target, typed parameter, mock payload, setup page, setup path, and setup value. Only the explicitly excluded persisted metadata in the source contract is absent.

`ROOT|page=<primaryPage>|class=<primaryClass>|primarySetup=<true|false>|pagesAndClasses=<canonicalTypedJSON>|namedPageEvidence=<canonicalTypedJSON>`

ROOT class equals `SG.rutClass`. `pagesAndClasses` is a canonical object containing the primary page-to-class mapping and every additional named page. `namedPageEvidence` is a canonical ordered array of `{ "evidence": <ID>, "page": <name>, "runtimeUse": <PAGE_PARAMETER|EXECUTABLE_PATH|PAGE_CREATION> }` objects and is empty only when no additional named page exists. This is the frozen source for primary setup, Page-and-Class projection, Scenario context, APB roots, and Generator metadata.

`TARGET|id=<ID>|order=<N>|source=<sortedRawSourceIDs>|behavior=<originalRUTBehavior>|constraint=<constraintOrAbsent>|state=<REQUIRED|BLOCKED|UNREACHABLE|EQUIVALENT>|proof=<proofOrAbsent>`

TARGET records are the self-contained projection of original-RUT coverage targets relevant to this physical group. Every ID in a Scenario `covers` field resolves to one REQUIRED TARGET in the same payload. A REQUIRED target must be covered by at least one Scenario. BLOCKED, UNREACHABLE, and EQUIVALENT targets require proof and cannot appear in `covers`. Dependencies never own TARGET records.

`COLUMN|id=<ID>|order=<N>|path=<exactInputPath>|class=<class>|mode=<mode>|source=<PRIMARY|PARAM|PAGE>|simulatedRoot=false`

WHEN uses one ordered COLUMN signature shared by every Scenario in the same physical group. STANDARD has none. Each WHEN Scenario has exactly one DECISION_INPUT INPUT and one DecisionInput ASSERT per COLUMN in identical order, with exact path/class/mode/value equality; it also has exactly one DecisionResult ASSERT. DecisionInput and DecisionResult `row` equals the Scenario's local order. No COLUMN or physical input path may be rooted in a simulated Data Page target. Different physical groups with unequal simulation keys may have different COLUMN signatures; cross-group signature equality is neither required nor inferred.

`COMPLEXITY|invocationCount=<N>|whenRuleReferenceCount=<N>|maxNesting=<N>|operationCount=<N>|loopCount=<N>|modifiedPropertyCount=<N>|conditionalBlockCount=<N>|pageParameterCount=<N>|unresolvedCriticalDependencyCount=<N>|invocationChainDepth=<N>|weightedScore=<number>|tier=<STANDARD|ELEVATED|HIGH>|ruleCrawlerCalls=<N>|dependencyReferencesRequested=<N>|hardTriggers=<sortedCodesOrAbsent>|triggeredLimits=<sortedCodesOrAbsent>|confidenceCap=<High|Medium|Low>|testabilityCap=<Testable|PartiallyTestable>`

For consumer validation only, use these exact arithmetic definitions on the recorded nonnegative integer metrics; do not reacquire semantic facts or change a recorded count. weightedScore = invocationCount*8 + whenRuleReferenceCount*6 + maxNesting*5 + operationCount*0.25 + loopCount*10 + modifiedPropertyCount*3 + pageParameterCount*4 + conditionalBlockCount*4 + unresolvedCriticalDependencyCount*12. The exact hard-trigger code/threshold pairs are INVOCATION_COUNT: invocationCount>=10; WHEN_RULE_REFERENCE_COUNT: whenRuleReferenceCount>=15; MAX_NESTING: maxNesting>=6; LOOP_COUNT: loopCount>=5; MODIFIED_PROPERTY_COUNT: modifiedPropertyCount>=20; UNRESOLVED_CRITICAL_DEPENDENCY_COUNT: unresolvedCriticalDependencyCount>=1; PAGE_PARAMETER_COUNT: pageParameterCount>=5; INVOCATION_CHAIN_DEPTH: invocationChainDepth>=6. Include LOOP_INVOCATION_COMBINATION exactly when loopCount>=1 and invocationCount>=1. hardTriggers is the sorted complete set, with no extra/missing trigger. Reject a mismatch in recorded score/triggers/tier/caps/limits; never repair those immutable semantic facts.

DEC-020 closes its two under-specified outputs. The phrase `loop+invocation combination requires it` means `loopCount >= 1 AND invocationCount >= 1`; this is the conservative HIGH trigger `LOOP_INVOCATION_COMBINATION`. Tier is HIGH when score is at least 50, any hard trigger exists, the loop/invocation trigger applies, `invocationChainDepth >= 2`, or `whenRuleReferenceCount >= 3 AND modifiedPropertyCount >= 8`; otherwise it is ELEVATED when `25 <= score < 50` and STANDARD below 25. Caps are derived, never selected: STANDARD maps to `High/Testable`, ELEVATED to `Medium/Testable`, HIGH to `Medium/PartiallyTestable`, and any unresolved critical dependency further lowers the HIGH confidence cap to `Low`. The checker recomputes score, trigger codes, tier, and both caps. `triggeredLimits` uses only `RULECRAWLER_CALL_CAP` at 120 calls and `RULES_TOTAL_REQUESTED_CAP` at 260 requested references. Complexity may increase trace depth and cap confidence/testability, but cannot remove coverage or final claims by itself.

`SCENARIO|id=<ID>|order=<N>|name=<name>|owner=<owner>|covers=<sortedTargetIDs>|testability=<Testable|PartiallyTestable|NotTestable>|confidence=<High|Medium|Low>`

Every final physical Scenario appears once. Scenario order is contiguous and stable. `covers` is non-empty and names original-RUT coverage targets, never dependency-owned targets.

### Physical Inputs and Setup

`PARAM|scenario=<ID>|id=<ID>|order=<N>|invocation=<sequenceID>|dependency=<RUTOrRuleName>|name=<parameterName>|formalType=<exactPegaTypeOrAbsent>|formalEvidence=<evidenceIDOrAbsent>|mode=<explicit|inherited|empty|not_applicable>|inheritance=<enabled|disabled|n_a>|expression=<rawExpressionOrAbsent>|valueType=<string|boolean|number|null|empty|json|absent>|value=<typedValueOrAbsent>|evidence=<evidenceIDs>`

Every behavior-affecting RUT, dependency, and Data Page parameter has one PARAM. Resolution follows explicit expression, then inheritance, then typed empty/null when inheritance is disabled; unresolved values are not guessed and must drive a gap/testability decision.

`INPUT|scenario=<ID>|id=<ID>|order=<N>|role=<PARAM|PRIMARY|PAGE|DECISION_INPUT>|path=<exactPath>|page=<pageOrAbsent>|class=<classOrAbsent>|mode=<mode>|valueType=<string|boolean|number|null|empty|json>|value=<typedValue>|resolution=<paramIDOrAbsent>|evidence=<evidenceIDs>`

`SETUP|scenario=<ID>|id=<ID>|order=<N>|role=<SETUP|DTA_BEFORE|PAGE_AND_CLASS>|path=<exactPath>|page=<page>|class=<class>|mode=<mode>|valueType=<string|boolean|number|null|empty|json>|value=<typedValue>|evidence=<evidenceIDs>`

Paths preserve namespace, leading dot, indices, keys, spelling, casing, and frozen primary root. `valueType=empty` requires the literal decoded value `<EMPTY>` and represents an initialized empty cell, not Page non-existence. `valueType=json` is canonical minified typed JSON. Reserved system pages are forbidden carriers.

Reserved top-level system-page seed/input ban (original Main 20–24): the closed roots are `pxProcess`, `AccessGroup`, `Application`, `OperatorID`, `Org`, `OrgDivision`, `pxRequestor`, and `pxThread`. Reject a source using any of them as ROOT.page, a ROOT.pagesAndClasses/namedPageEvidence page, INPUT/SETUP page or absolute input/seed path root, COLUMN or DecisionInput absolute path root, a PAGE-typed RUT/action parameter value, an action target page, or a SIM.setupPages page name/absolute seed-path root. Generator checks this source gate before any structural Knowledge, candidate write or Validator call. A leading-dot property path is relative to its already-validated page; a nested property token or literal scalar value named pxThread/OperatorID/etc. is not a forbidden top-level page. Never replace the root or delete the input to make the source runnable. Generator returns a terminal malformed-source result; only Author may revisit witness formation.

An INPUT sourced from a RUT parameter has one matching PARAM reference with identical typed value. A SIM references exactly the PARAM rows for its normalized parameter object. A non-parameter INPUT uses an absent resolution; SETUP has no resolution field.

Formal RUT parameter provenance (IPM-AUTH-035/IPM-AUTH-078; DEC-026):

- Every INPUT whose path begins with the exact namespace `Param.` is a physical formal RUT parameter carrier and must use `role=PARAM`, or `role=DECISION_INPUT` in a WHEN group. PRIMARY/PAGE roles cannot disguise that namespace; DECISION_INPUT is forbidden in STANDARD. Conversely, every `role=PARAM` INPUT must use that namespace. Every such INPUT resolves to one PARAM with `dependency=RUT` and exact `path=Param.<PARAM.name>`. Each name and resolution occurs once per Scenario. COLUMN `source=PARAM` is equivalent to this namespace; primary/property input bindings and dependency/Data Page parameters are not formal RUT arguments.
- Each formal carrier's PARAM has one `formalEvidence` EVIDENCE ID included in its `evidence` set. Copy `formalType` from the unique exact-name match in original `RuleJSON.pyParameters[].pyParametersParamType`, preserving spelling/case; never infer it from `valueType`, INPUT.mode, a resolved value, a dependency signature, or another parameter. Non-formal PARAM records have absent formalType and formalEvidence.
- The referenced EVIDENCE has `kind=RUT`, `source=RuleJSON/pyParameters/<zeroBasedArrayIndex>`, and a canonical typed JSON fact with exactly `pyParametersParamName` and `pyParametersParamType`. The fact name and type equal PARAM.name and PARAM.formalType. A missing/unusable non-string type is represented as JSON null in the fact and absent formalType; an explicit string, including an unsupported or empty string, is retained exactly. If the complete original array has no unique name match, use source `RuleJSON/pyParameters` and a null type instead of inventing an index. This array-level evidence records failed exact-name resolution, not a successful declaration. One indexed source cannot identify different definitions; one formal name cannot identify different source locations across Scenarios in a group.
- String arguments require a string or initialized-empty value; Integer requires an integral numeric value; Decimal requires a numeric value; Boolean/TrueFalse requires a typed boolean; PAGE requires a nonempty string naming an evidenced page in ROOT.pagesAndClasses. Formal metadata and physical value remain separate immutable facts. PAGE names are carried unchanged and never treated as quoted scalar strings. The complete downstream formatting table remains Generator-owned; this metadata capture does not authorize Scenario Author to serialize RuleCode.
- Missing/unknown/unsupported type, incompatible typed value, or unavailable PAGE carrier is a projection gap. Retain the frozen records and add GAP `code=RUT_PARAMETER_PROJECTION_UNAVAILABLE`, `scope=Param.<name>`, `effect=PARTIAL`, citing formalEvidence. The Scenario cannot be marked Testable; reflect the gap in SUMMARY and its complete blockingGaps census. Even with no external dependencies, any remaining GAP prevents dependencyClosureStatus=Closed. Generator must report that Scenario as unprojectable under its scoped failure contract; it cannot guess a type, omit only the parameter while keeping a runnable Scenario, change its value, or silently use a scalar representation. No coverage target or frozen Scenario is removed by metadata capture.

### Execution and Evidence

`RX|scenario=<ID>|id=<ID>|order=<N>|source=<sourceID>|operation=<operation>|context=<context>|guard=<guardOrAbsent>|inputs=<inputIDsOrAbsent>|result=<result>|writes=<pathsOrAbsent>|evidence=<evidenceIDs>`

`DEP|scenario=<ID>|id=<ID>|order=<N>|kind=<RUF|DP|HELPER|DT|NOT_APPLICABLE>|identity=<canonicalIdentity>|state=<CLOSED|KEYONLY|MISSING|LIMIT|OMIT_NONCRITICAL|NOT_APPLICABLE>|parameters=<canonicalTypedJSONOrAbsent>|proof=<proof>|evidence=<evidenceIDs>`

`BRANCH|scenario=<ID>|id=<ID>|order=<N>|source=<sourceID>|logic=<exactLogic>|inputs=<inputIDsOrAbsent>|result=<TRUE|FALSE|UNKNOWN|NOT_APPLICABLE>|writes=<pathsOrAbsent>|evidence=<evidenceIDs>`

`PRODUCER|scenario=<ID>|id=<ID>|order=<N>|target=<fullPath>|operation=<operation>|context=<context>|guard=<branchIDOrAbsent>|payload=<typedPayload>|execution=<rxID>|evidence=<evidenceIDs>`

`PROPERTY|scenario=<ID>|id=<ID>|order=<N>|target=<fullPath>|support=<Verified|PredictedFromRules|Structural|Omitted>|deterministic=<true|false>|valueType=<string|boolean|number|null|empty|json|absent>|value=<typedValueOrAbsent>|producers=<producerIDsOrAbsent>|evidence=<evidenceIDs>`

`EVIDENCE|scenario=<ID>|id=<ID>|order=<N>|kind=<RUT|DEPENDENCY|EXECUTION|SEED|COVERAGE|GATE>|source=<sourceIdentity>|fact=<groundedFact>|support=<Verified|PredictedFromRules|Structural>|confidence=<High|Medium|Low>`

`GAP|scenario=<ID>|id=<ID>|order=<N>|dependency=<depIDOrAbsent>|code=<gapCode>|scope=<targetOrClaim>|effect=<OMITTED|DOWNGRADED|PARTIAL>|evidence=<evidenceIDs>`

Every Scenario has at least one `RX`, `DEP`, `BRANCH`, `EVIDENCE`, and `NARRATIVE` record. Use the explicit `NOT_APPLICABLE` values rather than omitting a whole semantic category. Active dependency states are forbidden; only `CLOSED` or terminal gap states may be materialized. Positive exact claims must be supported by closed dependencies and producer execution.

### Decision Table Records

`DTM|scenario=<ID>|id=<ID>|order=<N>|source=<decisionTableKey>|mode=<FIRST_MATCH|EVALUATE_ALL>|scalarEnabled=<true|false>|evidence=<evidenceIDs>`

`DTE|scenario=<ID>|id=<ID>|order=<N>|dtm=<ID>|status=<EXECUTED|NOT_EXECUTED>|scalarState=<VALUE|NONE>|scalarType=<string|boolean|number|null|absent>|scalarValue=<typedValueOrAbsent>|actions=<dtaIDsOrAbsent>|consumers=<dtcIDsOrAbsent>|evidence=<evidenceIDs>`

`DTA|scenario=<ID>|id=<ID>|order=<N>|dte=<ID>|target=<fullPath>|page=<invocationPage>|class=<invocationClass>|operation=<SET|ADD|REMOVE|CLEAR>|beforeType=<string|boolean|number|null|empty|json|absent>|before=<typedValueOrAbsent>|afterType=<string|boolean|number|null|empty|json|absent>|after=<typedValueOrAbsent>|status=<EXECUTED|NOT_EXECUTED>|evidence=<evidenceIDs>`

`DTC|scenario=<ID>|id=<ID>|order=<N>|dte=<ID>|target=<consumerTarget>|decision=<assertOrOmitID>|evidence=<evidenceIDs>`

`DTRA|scenario=<ID>|id=<ID>|order=<N>|dte=<ID>|source=<decisionTableKey>|removedScalar=<targetsOrAbsent>|checkedActions=<dtaIDsOrAbsent>|omitted=<omitIDsOrAbsent>|pass=<true|false>|evidence=<evidenceIDs>`

If no Decision Table affects a Scenario, all five DT record types are absent. Otherwise each DTE references one DTM; its `actions` and `consumers` exactly enumerate the matching DTA and DTC records. Each DTC binds one scalar consumer target to the exact ASSERT or OMIT decision. For `scalarState=NONE`, every consumer is an OMIT with the DTM-mode-specific DEC-016 reason, no ASSERT exists for that target, DTRA `removedScalar` and `omitted` exactly equal the DTC targets and decisions, and no scalar propagation remains. For `scalarState=VALUE`, each consumer resolves to a value-consistent ASSERT.

Every DTA is listed in exactly one DTE and exactly one passing DTRA `checkedActions`. Any executed DTA with a non-absent before value has an exact `SETUP role=DTA_BEFORE` match on invocation page, class, target, type, and value. Every executed DTA final effect has a value-consistent PROPERTY plus ASSERT/OMIT decision on the same invocation page/class independent of scalar state. Thus Generator never recomputes a Decision Table result or drops an independent action.

### Simulation Decisions

`SIM|id=<ID>|rule=<dataPageOrRule>|sig=<DP_SIG>|shape=<page|list>|method=DefineData|class=<class>|itemClass=<itemClassOrAbsent>|params=<normalizedParams>|target=<targetPath>|mockingRuleType=<ruleType>|referredFromClass=<classOrAbsent>|setupPages=<canonicalTypedJSON>|scenario=<ID>|order=<N>|payload=<canonicalTypedJSON>|parameterResolutions=<paramIDs>|evidence=<evidenceIDs>`

The leading fields intentionally preserve the canonical cross-agent trace grammar. `sig=<DP_SIG>` and `params=<normalizedParams>` are mandatory, non-empty, exact frozen values. `params`, `setupPages`, and `payload` are canonical minified typed JSON. `setupPages` has the same exact array shape used in the group key. `shape=list` requires non-absent `itemClass`; `shape=page` permits absent `itemClass`. Every reachable or unknown Thread-level DP signature has exactly one SIM decision in its Scenario. Excluded-scope Data Pages instead produce an explicit gap/downgrade or a new witness; `NO_SIMULATION` is never a SIM signature.

For WHEN, each Scenario's ordered SIM records serialize to the complete `simulationGroupKey` entry set; every declared key field is compared, not only signature and parameters. A `NO_SIMULATION` group contains zero SIM records in every Scenario.

UnitTestGenerator must project every SIM record mechanically to exactly one matching `pySimulation` entry. Validator must compare `rule`, `sig`, `shape`, `method`, `class`, `itemClass`, `params`, and `target` against that exact entry. S3 and S4 must update both consumers from this same grammar; any field drift is blocking.

### Assertion and Omission Decisions

Standard assertion form:

`ASSERT|id=<ID>|kind=<Property|Page|List|ResultCount>|target=<path>|page=<pageOrAbsent>|class=<class>|mode=<propertyMode>|comparator=<comparator>|value=<typedExpectedValueOrAbsent>|support=<Verified|PredictedFromRules|Structural>|scenario=<ID>|order=<N>|producer=<producerIDOrAbsent>|evidence=<evidenceIDs>`

Rule-Obj-When DecisionInput form:

`ASSERT|id=<ID>|kind=DecisionInput|row=<N>|target=<exactInputPath>|page=rowLevelPage|class=<class>|mode=<mode>|comparator=Input Value|value=<valueOrEMPTY>|support=<Verified|PredictedFromRules|Structural>|scenario=<ID>|order=<N>|producer=<producerIDOrAbsent>|evidence=<evidenceIDs>`

Rule-Obj-When DecisionResult form:

`ASSERT|id=<ID>|kind=DecisionResult|row=<N>|target=Result|page=rowLevelPage|class=<class>|mode=text|comparator=Is Equals To|value=<true|false>|support=<Verified|PredictedFromRules>|scenario=<ID>|order=<N>|producer=<producerIDOrAbsent>|evidence=<evidenceIDs>`

`OMIT|id=<ID>|target=<pathOrClaim>|reason=<reasonCode>|scenario=<ID>|order=<N>|evidence=<evidenceIDs>`

Allowed `reason` values are exactly:

- `unresolved_external_source`
- `unavailable_rulejson_after_limit_exhaustion`
- `unresolvable_runtime_input`
- `inactive_evaluate_all_scalar`
- `inactive_return_values_scalar`
- `schema_incompatible_assertion_target`
- `redundant_iteration_coverage`
- `incorrect_candidate_assertion`

Every enumerated final claim has exactly one ASSERT or OMIT. Exact-value ASSERT records use only `Verified` or `PredictedFromRules`. Structural records cannot invent values. DecisionInput paths and empty values remain exact. ASSERT/SIM/OMIT IDs are unique within a Scenario.

When UnitTestGenerator creates `AssertionDecisionTrace`, it uses exact tag-specific whitelists rather than subtracting fields. SIM is exactly `SIM|id|rule|sig|shape|method|class|itemClass|params|target`. Standard ASSERT is exactly `ASSERT|id|kind|target|page|class|mode|comparator|value|support`. DecisionInput and DecisionResult ASSERT are exactly `ASSERT|id|kind|row|target|page|class|mode|comparator|value|support`. OMIT is exactly `OMIT|id|target|reason`. Fields are pipe-joined as `key=value` after the tag in that declared order. Therefore ScenarioGroup-only `mockingRuleType`, `referredFromClass`, `setupPages`, `scenario`, `order`, `payload`, `parameterResolutions`, `producer`, and `evidence` never enter the trace. Inside trace values UnitTestGenerator encodes `&` as `&amp;`, then `|` as `&#124;`, CR as `&#13;`, LF as `&#10;`, and double quote as `&quot;`; an absent ledger value becomes `-`. Validator reverses the same trace encoding. The checker proves a positive SIM projection and rejects an added non-whitelisted field. This trace encoding is distinct from outer ledger escaping and is synchronized in S3/S4.

### Narrative and Completion

`SUMMARY|scenario=<ID>|id=<ID>|order=1|supportLevel=<Verified|PredictedFromRules|StructuralOnly|OmittedClaimsPresent|NotTestable>|dependencyState=<AllResolved|SomeUnresolved|NotApplicable>|branchState=<AllEvaluated|SomeUnknown|NotApplicable>|simulationState=<NotRequired|RequiredAndAligned|RequiredButLimited|NotApplicable>|complexityTier=<STANDARD|ELEVATED|HIGH>|assertionCount=<N>|omissionCount=<N>|simulationCount=<N>|gapCount=<N>|internalChecklist=<sortedGateCodes>|reasoningEvidence=<evidenceIDs>|dependencyEvidence=<evidenceIDsOrAbsent>|blockingGaps=<gapIDsOrAbsent>|dependencyClosureStatus=<Closed|Blocked>|maxDependencyWaveReached=<N>|queuedDependencyCount=0|unscannedFetchedRuleJsonCount=0|seedCoverageEvidence=<evidenceIDsOrAbsent>`

SUMMARY is the structured source for mechanically projected EvidenceSummary facts. Counts equal the Scenario's final records. `Closed` requires only CLOSED/NOT_APPLICABLE dependencies and no gaps; `Blocked` requires terminal dependency states and matching gaps. Active ready/queued/unscanned work is unrepresentable. `complexityTier` equals the group COMPLEXITY tier; Scenario confidence/testability honor its caps, including `NotTestable` when no meaningful assertion remains. Evidence and gap references resolve without free-text inference.

`internalChecklist` uses only the sorted codes `CELLS`, `COVERAGE`, `DECISION_TABLE`, `DEPENDENCY`, `ROOT`, `SEED`, and `SIMULATION`, including every code applicable to the Scenario. `supportLevel` is `NotTestable` when Scenario testability is NotTestable, otherwise `OmittedClaimsPresent` when any final claim is omitted, otherwise the highest ASSERT support with `Structural` mapped to `StructuralOnly`. `blockingGaps` is the exact GAP census for a Blocked summary and absent for Closed. Branch, simulation, dependency-wave, and record counts are recomputed rather than accepted as narrative claims.

`NARRATIVE|scenario=<ID>|id=<ID>|order=1|text=<oneOrTwoFactualSentences>|evidence=<evidenceIDs>`

`END|targetCount=<N>|columnCount=<N>|paramCount=<N>|scenarioCount=<N>|inputCount=<N>|setupCount=<N>|rxCount=<N>|depCount=<N>|branchCount=<N>|producerCount=<N>|propertyCount=<N>|dtCount=<N>|simCount=<N>|assertCount=<N>|omitCount=<N>|evidenceCount=<N>|gapCount=<N>|summaryCount=<N>|narrativeCount=<N>|complete=PASS`

END counts cover the whole payload. `dtCount` is the combined count of DTM, DTE, DTA, DTC, and DTRA records. A parser recomputes every count and rejects mismatch.

## Completeness Gate

Before `WriteMemory`, Scenario Author must parse its own final payload and prove all of the following:

- exact version, record grammar, order, arity, escaping, IDs, references, and END counts;
- header identity matches exact CaseID and immutable original RUTType;
- STANDARD/WHEN cardinality and typed simulation-group key rules;
- coverage targets are complete, original-RUT-owned, and match the audited frozen compiler snapshot;
- every Scenario has physical inputs/setup, execution, dependencies, branch state, producer/property facts, final ASSERT/SIM/OMIT decisions, evidence, gaps, confidence/testability, and narrative as applicable;
- dependency work is closed or terminal, with no active crawl state or transient draft/planning record;
- ASSERT/SIM/OMIT census is complete and all exact claims have producer/evidence support;
- Decision Table records and the two inactive-scalar omission reasons are atomically consistent;
- no UnitTestRules, RuleCode, schema-selection, Validator, candidate, repair, MemoryTemp, or response-record responsibility is present.

Failure restarts the earliest invalid semantic phase or terminates the run; it never writes a partial payload.

## Static Fixture Set

The repository fixtures under `fixtures/s2/` are normative examples for contract validation, not Pega runtime proof:

- `standard-escaping.sgl`: one non-When Scenario and lossless pipe/newline/tab/backslash content;
- `standard-not-testable.sgl`: a zero-parameter, NotTestable Scenario with NotApplicable simulation and an executed Decision Table effect resolved by OMIT;
- `when-key-a.sgl`: two homogeneous When Scenarios sharing one typed simulation key;
- `when-key-b.sgl`: a different runtime-complete typed key that must remain a separate physical group;
- `when-no-simulation.sgl`: the exact common `NO_SIMULATION` group representation;
- `orchestration.json`: stable group/write/UUID order, exact call arguments, write-failure no-retry/no-handoff behavior, and Generator Completed/PartiallyCompleted/Failed/malformed outer mappings.

Run `python scripts/validate_s2_design.py`. The checker verifies the fixture ledgers, orchestration expectations, and the 106-row implementation slice. Passing results are repository-static evidence only.

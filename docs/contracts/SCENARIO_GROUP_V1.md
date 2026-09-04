# ScenarioGroup v1 Contract

- **Owner:** Scenario Author
- **Consumers:** UnitTestGenerator and, through generated trace projection, Validator
- **Transport:** `WriteMemory(CaseID, Type="ScenarioGroup", Payload)`
- **Contract status:** `VERIFIED` by the final focused independent S2 follow-up on 2026-09-04
- **Runtime status:** repository-static only; Pega tool implementation and runtime proof are external under DEC-019

## Purpose and Boundary

A ScenarioGroup payload is the complete, immutable semantic snapshot for exactly one physical unit-test group. It is not candidate JSON, does not contain `UnitTestRules` or `RuleCode`, and cannot ask UnitTestGenerator to crawl, infer expected values, alter grouping, or make new ASSERT/SIM/OMIT decisions. UnitTestGenerator may only validate this contract and project its frozen facts.

Scenario Author writes one payload for each final physical group, in stable group order. It calls `WriteMemory` once per group with the exact CaseID, Type `ScenarioGroup`, and payload bytes. It preserves each returned UUID opaquely. Only after every write succeeds does it call UnitTestGenerator exactly once with the exact CaseID, immutable original RUTType, and ordered UUID array. A failed or malformed write is terminal: no retry, no partial Generator call, and no deletion or overwrite of earlier immutable records.

The WriteMemory result envelope is the exact S1 contract: fields are exactly `Success` (boolean), `UUID` (string), `ErrorCode` (string), and `ErrorMessage` (string). `Success=true` requires a non-empty opaque UUID and empty error fields. `Success=false` requires an empty UUID, non-empty ErrorMessage, and ErrorCode `INVALID_INPUT`, `UNSUPPORTED_TYPE`, or `WRITE_FAILED`. Missing, additional, wrongly cased, wrongly typed, or contradictory fields are malformed and follow the same terminal no-retry/no-handoff path. UUID collection begins only after this complete envelope check.

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

ID assignment is deterministic and freeze-stable. TARGET and SCENARIO IDs are the exact final compiler `T` and `S` IDs. Group IDs are `G001`, `G002`, and so on after stable physical-group ordering. Other record IDs use the tag prefix plus a zero-padded three-digit occurrence number after the record's normative sort inside one Scenario (`C` COLUMN, `K` PARAM, `I` INPUT, `U` SETUP, `R` RX, `D` DEP, `B` BRANCH, `P` PRODUCER, `Y` PROPERTY, `Q` DT family, `Z` DTC, `M` SIM, `A` ASSERT, `O` OMIT, `E` EVIDENCE, `X` GAP, `H` SUMMARY, `N` NARRATIVE). Identical frozen semantics rematerialize identical IDs. A semantic or grouping change returns to WITNESSES, rebuilds the complete snapshot, and reassigns group/local order atomically; consumers never patch IDs in place.

## Required Record Order

Records are sorted by this sequence:

1. one `SG` and one `ROOT`;
2. all `TARGET` records in original-RUT inventory order;
3. zero `COLUMN` records for STANDARD, or one or more ordered `COLUMN` records for WHEN;
4. one `COMPLEXITY` record;
5. all `SCENARIO` records by scenario order;
6. for each scenario, its `PARAM`, `INPUT`, `SETUP`, `RX`, `DEP`, `BRANCH`, `PRODUCER`, `PROPERTY`, `DTM`, `DTE`, `DTA`, `DTC`, `DTRA`, `SIM`, `ASSERT`, `OMIT`, `EVIDENCE`, `GAP`, `SUMMARY`, and `NARRATIVE` records in that tag order and then record order;
7. one `END`.

No unknown record, field, or duplicate `(scenario,id)` is allowed. All references resolve inside the same payload. The payload is a complete replacement snapshot; no consumer may combine it with an older ScenarioGroup or a private scenario ledger.

## Record Grammar

The following forms are exact. A field containing `-` is nullable only when its definition below says so.

### Group and Scenario

`SG|version=1|caseId=<CaseID>|rutType=<originalRUTType>|rutClass=<class>|rutName=<name>|ruleset=<ruleset>|groupId=<ID>|groupOrder=<N>|kind=<STANDARD|WHEN>|scenarioCount=<N>|simulationGroupKey=<canonicalKeyOrAbsent>`

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

The metric names, hard-trigger thresholds, and weighted-score formula are exactly those in the canonical Author complexity contract. DEC-020 closes its two under-specified outputs. The phrase `loop+invocation combination requires it` means `loopCount >= 1 AND invocationCount >= 1`; this is the conservative HIGH trigger `LOOP_INVOCATION_COMBINATION`. Tier is HIGH when score is at least 50, any hard trigger exists, the loop/invocation trigger applies, `invocationChainDepth >= 2`, or `whenRuleReferenceCount >= 3 AND modifiedPropertyCount >= 8`; otherwise it is ELEVATED when `25 <= score < 50` and STANDARD below 25. Caps are derived, never selected: STANDARD maps to `High/Testable`, ELEVATED to `Medium/Testable`, HIGH to `Medium/PartiallyTestable`, and any unresolved critical dependency further lowers the HIGH confidence cap to `Low`. The checker recomputes score, trigger codes, tier, and both caps. `triggeredLimits` uses only `RULECRAWLER_CALL_CAP` at 120 calls and `RULES_TOTAL_REQUESTED_CAP` at 260 requested references. Complexity may increase trace depth and cap confidence/testability, but cannot remove coverage or final claims by itself.

`SCENARIO|id=<ID>|order=<N>|name=<name>|owner=<owner>|covers=<sortedTargetIDs>|testability=<Testable|PartiallyTestable|NotTestable>|confidence=<High|Medium|Low>`

Every final physical Scenario appears once. Scenario order is contiguous and stable. `covers` is non-empty and names original-RUT coverage targets, never dependency-owned targets.

### Physical Inputs and Setup

`PARAM|scenario=<ID>|id=<ID>|order=<N>|invocation=<sequenceID>|dependency=<RUTOrRuleName>|name=<parameterName>|mode=<explicit|inherited|empty|not_applicable>|inheritance=<enabled|disabled|n_a>|expression=<rawExpressionOrAbsent>|valueType=<string|boolean|number|null|empty|json|absent>|value=<typedValueOrAbsent>|evidence=<evidenceIDs>`

Every behavior-affecting RUT, dependency, and Data Page parameter has one PARAM. Resolution follows explicit expression, then inheritance, then typed empty/null when inheritance is disabled; unresolved values are not guessed and must drive a gap/testability decision.

`INPUT|scenario=<ID>|id=<ID>|order=<N>|role=<PARAM|PRIMARY|PAGE|DECISION_INPUT>|path=<exactPath>|page=<pageOrAbsent>|class=<classOrAbsent>|mode=<mode>|valueType=<string|boolean|number|null|empty|json>|value=<typedValue>|resolution=<paramIDOrAbsent>|evidence=<evidenceIDs>`

`SETUP|scenario=<ID>|id=<ID>|order=<N>|role=<SETUP|DTA_BEFORE|PAGE_AND_CLASS>|path=<exactPath>|page=<page>|class=<class>|mode=<mode>|valueType=<string|boolean|number|null|empty|json>|value=<typedValue>|evidence=<evidenceIDs>`

Paths preserve namespace, leading dot, indices, keys, spelling, casing, and frozen primary root. `valueType=empty` requires the literal decoded value `<EMPTY>` and represents an initialized empty cell, not Page non-existence. `valueType=json` is canonical minified typed JSON. Reserved system pages are forbidden carriers.

An INPUT sourced from a RUT parameter has one matching PARAM reference with identical typed value. A SIM references exactly the PARAM rows for its normalized parameter object. A non-parameter INPUT uses an absent resolution; SETUP has no resolution field.

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

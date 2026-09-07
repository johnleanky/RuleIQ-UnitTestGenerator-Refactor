# ExecPlan: S0 Baseline and Contract Stabilization

- **Roadmap stage:** `S0`
- **Plan status:** `CLOSED`
- **Last reconciled:** 2026-09-03

## Purpose

Establish a trustworthy, restart-safe baseline, complete preservation traceability for the current monolithic instructions, and decision-complete contracts before any Memory, agent, Validator, prompt, schema, or Pega export refactor begins.

## Scope

- Initialize and validate the five-file repository continuity framework.
- Build and independently review the Instruction Preservation Matrix before changing any product prompt.
- Correct the verified syntax defect in the standard JSON example without changing its schema.
- Parse both schemas and examples with BOM-aware tooling and validate each example against its matching schema using already available tools.
- Record canonical integrity for `Main_Agent_Prompt.txt` and establish repeatable `<pySystemPrompt>` boundary and decoded-equivalence checks for the in-scope Validator pair only.
- Define sufficient interfaces and ownership boundaries for S1 through S4. DEC-019 later supersedes the repository-owned Pega tool implementation assumption while preserving the caller-facing contracts.
- Apply the high-risk change gate after every qualifying change or indivisible batch.
- Obtain an independent read-only validation report before stage closure.

## Excluded Scope

- Product implementation of Memory tools or UUID-aware JsonValidationTool; DEC-019 later confirms this remains external to the repository.
- Scenario Author, Unit Test Generator, or Validator prompt refactoring.
- Modification or parity enforcement of the legacy `Main_Agent.txt` Pega rule export; it is reference-only.
- Creation or synthetic modification of Pega agent system metadata.
- Schema contract changes unless separately approved after a verified incompatibility.
- Dependency installation, pre-closure Git commit, push, pull request, deployment, or Pega environment mutation. The root agent may create the initial baseline commit only after S0 closes.

## Assumptions and Unknowns

- The accepted decisions in `docs/decisions/DECISIONS.md` are authoritative for target architecture.
- Existing root artifacts are current-state evidence, even where they describe the legacy architecture.
- The root agent is authorized to create the initial baseline commit after, but not before, verified S0 closure.
- Local schema-keyword conformance of both examples is `VERIFIED` by independent Python and Node implementations; reproduction with a complete installed Draft 2020-12 or Pega validator remains unavailable and is not claimed.
- No usable exports exist for the new Memory tools, UUID-aware validation tool, or Generator. S0 defines their contracts; under later DEC-019 the user creates the external tool implementations, while S3 retains repository-owned Generator design and creation.
- The new Generator rule name is `UnitTestGenerator`; use `UnitTestGenerator_Prompt.txt` as its canonical prompt and `UnitTestGenerator.txt` as its export.

## Dependencies

- Repository root and current artifacts.
- Accepted architecture decisions.
- Existing local JSON parsing or Pega validation capabilities; no dependency installation is permitted.
- No prior Roadmap stage.

## Milestones

1. Initialize and validate the continuity framework.
2. Inventory and classify every normative monolith instruction and affected Validator contract in the Instruction Preservation Matrix.
3. Obtain independent matrix-coverage validation and resolve every blocking finding.
4. Correct and parse the standard JSON example.
5. Validate both schema/example families without installing dependencies.
6. Record the canonical Main prompt baseline and verify Validator prompt/export synchronization and baseline artifact integrity.
7. Confirm accepted architecture contracts and from-scratch artifact design constraints are sufficient to begin S1.
8. Obtain independent read-only validation before closing S0.
9. After S0 is closed, create the user-authorized initial baseline commit before starting S1 work.

## Progress

- `VERIFIED` — repository root, branch, unborn HEAD, remote state, working tree, and documentation inventory inspected.
- `VERIFIED` — standard example syntax failure reproduced at line 269.
- `VERIFIED` — continuity artifacts created, fully re-read, and checked for paths, links, English-only content, active-stage count, dependency cycles, decision fields and stage references, next-action count, and product-file scope.
- `VERIFIED` — instruction-preservation and high-risk independent-validation gates are documented; an independent read-only subagent returned `PASS` with no findings, and the root agent reconciled the report on 2026-09-02.
- `VERIFIED` — Instruction Preservation Matrix contains 106 Author rows and 44 affected Validator rows covering all normative headings and identified cross-cutting locks; independent reviews found trace, omission-catalog, coverage-claim, and ValidatorReport-destination defects, the root agent corrected them, and the final follow-up returned `PASS` with no findings on 2026-09-03.
- `VERIFIED` — independent matrix-coverage and ownership review completed with final `PASS` after required correction cycles.
- `VERIFIED` — the standard example comma defect is corrected; PowerShell, Python, and Node parse all four schema/example files successfully, and independent review returned `PASS`.
- `VERIFIED` — independent Python and Node validators covering all assertion keywords used by the two schemas report zero example-conformance errors; no installed full Draft 2020-12 or runnable Pega validator is available, and no dependency was installed.
- `VERIFIED` — canonical Main prompt baseline and Validator prompt/export decoded comparison. `Main_Agent_Prompt.txt` has a recorded hash and structural baseline; the Validator export has one boundary pair and matches the readable prompt after bounded fragment decoding and serializer-boundary whitespace normalization. `Main_Agent.txt` was excluded and untouched.
- `VERIFIED` — the S1 entry-contract audit and opaque-Payload/UUID decision passed independent review; no product decision or external artifact blocks S1 planning.
- `VERIFIED` — the first final independent S0 review found three documentation inconsistencies; the root corrected them, and focused independent follow-up returned `PASS` with no findings on 2026-09-03.
- `NOT_STARTED` — all product refactor work.

## Instruction Preservation Matrix

- **Status:** `VERIFIED` — all 150 source rows are mapped and the final independent coverage/ownership review returned `PASS`.
- **Inventory scope:** Every normative heading, subsection, standalone hard lock, source-of-truth rule, execution-order requirement, tool contract, ledger contract, grouping/cardinality rule, serialization rule, repair rule, limit, and completion gate in `Main_Agent_Prompt.txt`, plus every `Validator_Prompt.txt` contract affected by the split.
- **Coverage rule:** Every source item must have at least one matrix row. Cross-cutting items may have multiple rows only when `SPLIT` is required; the rows must define non-overlapping ownership.
- **Removal rule:** `REMOVE` is permitted only for `LEGACY_TRANSPORT` and must cite an accepted decision and replacement or retirement evidence.
- **Completion rule:** Matrix coverage must be 100%, with no unowned `STABLE` item, unresolved `CONFLICTING` item, or destination lacking a regression check.

Regression evidence codes:

- **E1:** semantic golden fixtures comparing monolith decisions with materialized ScenarioGroup records.
- **E2:** static ownership, tool-allowlist, and forbidden-responsibility audit.
- **E3:** versioned line-ledger grammar, escaping, completeness, replacement, and round-trip tests.
- **E4:** exact CaseID + Type + UUID Memory round trips, isolation, immutability, and failure tests.
- **E5:** standard-schema projection and schema-validation fixtures.
- **E6:** Rule-Obj-When grouping, MultInpComb, simulation, cardinality, and row-shape fixtures.
- **E7:** Validator routing, issue scope, repair, rejection, versioning, and retry-limit fixtures.
- **E8:** decoded canonical-prompt/Pega-export parity and export-boundary checks.
- **E9:** GeneratorRunReport and outer Scenario Author status-mapping tests.
- **E10:** RuleCrawler, KnowledgeTool, dependency-state, and ledger trace fixtures.
- **E11:** independent read-only review with forward and reverse matrix audit.

### Current Author inventory

| ID | Source | Stable behavior or invariant | Classification | Owner | Action | Target | Evidence | Status |
|---|---|---|---|---|---|---|---|---|
| IPM-AUTH-001 | Main 3–5, Core contract | Maximize evidence-supported RUT coverage with the minimum valid physical unit-test groups. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: purpose and semantic objective | E1,E11 | MAPPED |
| IPM-AUTH-002 | Main 7,14–18 | Structured-output limits require strict evidence, dependency closure, materialized semantics, and schema-governed projection; active crawl blocks authoring. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author semantic gates; Generator projection discipline | E1,E2,E5,E10 | MAPPED |
| IPM-AUTH-003 | Main 9–12 | Monolithic generation, persistence, validation, repair, and status handling must become ordered ScenarioGroup handoff, candidate generation, validation, and outer status mapping. | CONFLICTING | SHARED_CONTRACT | REPLACE | Scenario Author/Generator interface and runtime report | E2,E4,E7,E9 | MAPPED |
| IPM-AUTH-004 | Main 20–24, reserved-page ban | Reserved system pages are never setup, simulation, primary, P&C, or MultInpComb input roots; an invalid carrier cannot silently remove coverage. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: witness and seed safety | E1,E6 | MAPPED |
| IPM-AUTH-005 | Main 26–27, compiler memory authority | Scenario formation uses one complete replacement snapshot and no competing scenario ledger; replace MemoryTemp with final immutable ScenarioGroup records. | LEGACY_TRANSPORT | SCENARIO_AUTHOR | REPLACE | Scenario Author: compiler state and Memory handoff | E2,E3,E4 | MAPPED |
| IPM-AUTH-006 | Main 29–30, MultInpComb firewall | MultInpComb applies only to original Rule-Obj-When; non-When physical groups contain exactly one Scenario. | STABLE | SHARED_CONTRACT | MOVE | ScenarioGroup RUT-type and cardinality contract | E1,E5,E6 | MAPPED |
| IPM-AUTH-007 | Main 32–60, simulation key | Each When Scenario has one typed canonical key containing every runtime-relevant simulation field and concrete DP parameter; no simulation uses NO_SIMULATION. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: group formation and ScenarioGroup header | E1,E3,E6 | MAPPED |
| IPM-AUTH-008 | Main 61–96, grouping/cardinality | Equal simulation keys form one group, unequal keys never mix, order is stable, local rows are bijective, and unit count equals distinct keys. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author grouping; Generator one-entry projection | E1,E3,E6 | MAPPED |
| IPM-AUTH-009 | Main 99–123, visible output | Candidate and internal work stay hidden; Generator has a runtime report and Scenario Author emits only the bounded two-field external status. | STABLE | SHARED_CONTRACT | SPLIT | Generator report; Scenario Author outer response | E2,E9 | MAPPED |
| IPM-AUTH-010 | Main 126–132, forbidden final state | Internal ledgers, transport state, reports, and unsupported fields never enter schema-governed candidate JSON. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: candidate serialization exclusions | E5,E6,E7 | MAPPED |
| IPM-AUTH-011 | Main 136–159, stored-response validation loop | Validation starts a closed repair phase: no new crawl or semantic knowledge; repair uses immutable scenarios and current candidate only. | CONFLICTING | UNIT_TEST_GENERATOR | REPLACE | Generator: projection-only validation loop | E2,E7 | MAPPED |
| IPM-AUTH-012 | Main 161–167, candidate storage | A complete formatted candidate is persisted only after semantic and projection gates, using WriteMemory and a returned UUID. | LEGACY_TRANSPORT | UNIT_TEST_GENERATOR | REPLACE | Generator: UnitTestCandidate write | E4,E5,E7 | MAPPED |
| IPM-AUTH-013 | Main 165,171–177 | CaseID is GetCaseData.pyID and original RUTType is immutable across generation, validation, and repair. | STABLE | SHARED_CONTRACT | MOVE | Shared agent, Memory, and Validator interface | E4,E7 | MAPPED |
| IPM-AUTH-014 | Main 169–180 | Validator selects the schema family from immutable original RUTType; caller never passes or recomputes schema mode. | STABLE | VALIDATOR | MOVE | Validator: schema selection | E5,E6,E7 | MAPPED |
| IPM-AUTH-015 | Main 182–201, validator results | Preserve unaffected projection material; replace Author repair/rerun with Generator projection repair and semantic rejection. | CONFLICTING | UNIT_TEST_GENERATOR | REPLACE | Generator: validator route handler | E2,E7 | MAPPED |
| IPM-AUTH-016 | Main 203–223 | HUMAN or malformed reports terminate; useful issue messages precede bounded fallback failure text. | STABLE | SHARED_CONTRACT | SPLIT | Generator terminal handling; Scenario Author status mapping | E7,E9 | MAPPED |
| IPM-AUTH-017 | Main 225–239 | Mass projection failure rebuilds from unchanged ScenarioGroups; warnings do not block OK; write failure terminates; at most two repairs follow first report. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: rebuild and repair limit | E7 | MAPPED |
| IPM-AUTH-018 | Main 241, data bus | Large candidates and all validators address the same exact immutable UnitTestCandidate version. | LEGACY_TRANSPORT | SHARED_CONTRACT | REPLACE | UUID-addressed candidate Memory contract | E4,E7 | MAPPED |
| IPM-AUTH-019 | Main 245–253, interfaces | Tool access is role-bounded: Scenario Author analyzes/writes groups; Generator reads groups/writes candidates/calls Validator. | CONFLICTING | SHARED_CONTRACT | REPLACE | Role-specific tool allowlists | E2,E4 | MAPPED |
| IPM-AUTH-020 | Main 257–264, source order | Schema governs structure; RuleJSON governs semantics; immutable ScenarioGroups govern final scenarios; examples never override authorities. | STABLE | SHARED_CONTRACT | SPLIT | Shared authority hierarchy | E1,E2,E5,E7 | MAPPED |
| IPM-AUTH-021 | Main 268–305, Knowledge keys | Knowledge uses qualified canonical composite keys; MultInpComb UTC keys depend only on original When RUT type. | STABLE | SHARED_CONTRACT | MOVE | Shared KnowledgeTool contract | E5,E6,E10 | MAPPED |
| IPM-AUTH-022 | Main 307–324, knowledge cache | Parse pxResults, batch/cache each requested key once, record gaps, and prohibit new Knowledge acquisition after validation. | STABLE | SHARED_CONTRACT | SPLIT | Role-local caches; read-only repair phase | E2,E7,E10 | MAPPED |
| IPM-AUTH-023 | Main 326–339, required keys | Scenario Author owns semantic rule/dependency/property guidance; Generator owns UTC schema/example/RuleCode guidance. | STABLE | SHARED_CONTRACT | SPLIT | Role-specific required-key sets | E2,E5,E10 | MAPPED |
| IPM-AUTH-024 | Main 341–356, checkpoints | Knowledge calls occur only at deterministic batch checkpoints, never repeat, and missing guidance narrows claims instead of inviting inference. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author semantic checkpoints; Generator pre-projection checkpoint | E2,E7,E10 | MAPPED |
| IPM-AUTH-025 | Main 358–374, guided extraction | Knowledge guidance controls semantic extraction, context, parameters, properties, simulations, and RuleCode serialization according to role. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author semantics; Generator serialization | E1,E2,E5,E10 | MAPPED |
| IPM-AUTH-026 | Main 375–379 | Missing required guidance remains an explicit gap affecting support and testability; it is never treated as resolved. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author evidence/gap ledger | E1,E3,E10 | MAPPED |
| IPM-AUTH-027 | Main 382–395, execution 1–10 | Acquire/validate RUT identity, lock type, load guidance, scan/crawl, and prove closed or terminal dependencies before authoring. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: acquisition and crawl order | E1,E10 | MAPPED |
| IPM-AUTH-028 | Main 396–400, execution 11–15 | Semantic analysis, evidence, complexity, and Scenario Compiler freeze occur only after dependency closure. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: semantic authoring order | E1,E3,E10 | MAPPED |
| IPM-AUTH-029 | Main 400–413, packaging | Scenario Author fixes physical groups; Generator waits for them and performs exact one-entry-per-group projection. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup handoff and Generator packaging | E3,E5,E6 | MAPPED |
| IPM-AUTH-030 | Main 414–418, assertions | Enumerate candidates, apply the assertion ladder, and pass runtime/producer/simulation/closure gates before final semantic decisions. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: assertion finalization | E1,E3,E10 | MAPPED |
| IPM-AUTH-031 | Main 419–421 | RuleCode purpose, serialization, and post-RuleCode alignment audit are mandatory projection work. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: projection order and audit | E5,E6,E7 | MAPPED |
| IPM-AUTH-032 | Main 422–424 | Replace Author storage/Validator/repair with Generator candidate UUID, Validator invocation, projection-only repair, and report. | CONFLICTING | UNIT_TEST_GENERATOR | REPLACE | Generator orchestration | E2,E4,E7,E9 | MAPPED |
| IPM-AUTH-033 | Main 426–523, Internal Evidence Ledger and DWL | Complete the evidence ledger before RuleCode; one canonical dependency state machine governs identity, DP signatures, grammar, transitions, closure, and authoring gates; no parallel proof ledger. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author evidence/DWL and ScenarioGroup snapshot | E1,E3,E10 | MAPPED |
| IPM-AUTH-034 | Main 525–539, DependencyResolution | DependencyResolution is a read-only DWL projection; narrative dependencies without rows block authoring. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup dependency projection | E1,E3,E10 | MAPPED |
| IPM-AUTH-035 | Main 541–553, parameters | Every behavior-affecting parameter records invocation, mode, inheritance, expression, resolved value, and evidence; guessing is forbidden. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup parameter records | E1,E3 | MAPPED |
| IPM-AUTH-036 | Main 555–580, branches | Every relevant branch records exact logic, inputs, result, paths, and write reachability without mixing exclusive branches. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup branch/WR records | E1,E3 | MAPPED |
| IPM-AUTH-037 | Main 581–606, pyLogic lock | Copy pyLogic verbatim, tokenize every top-level clause, evaluate all clauses, discover dependencies, and block authoring on failure. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: When semantic gate | E1,E3,E10 | MAPPED |
| IPM-AUTH-038 | Main 608–676, RUT I/O lock | Compute root identity, reads/writes, required/forbidden seeds, conflicts, and pre-seed closure; never patch frozen scenarios. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: seed-direction gate | E1,E3 | MAPPED |
| IPM-AUTH-039 | Main 679–693, property traces | Every emitted or omitted exact claim records support, determinism, confidence, final value, and ordered producing modifications. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup property traces | E1,E3 | MAPPED |
| IPM-AUTH-040 | Main 695–707, omissions | Omission follows full candidate enumeration and assertion ladder, uses an allowed reason, and never cites complexity alone. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup OMIT decisions | E1,E3 | MAPPED |
| IPM-AUTH-041 | Main 709–736, limits | Complexity metrics, thresholds, caps, and tiers are deterministic; complexity increases trace depth but cannot alone reduce coverage. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: complexity and limits | E1,E3 | MAPPED |
| IPM-AUTH-042 | Main 738–770, runtime rows | Every execution-relevant step/expression/action has a grounded RX row; unknowns stay unknown and drive producer/DP projections. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup runtime execution rows | E1,E3,E10 | MAPPED |
| IPM-AUTH-043 | Main 774–787, discovery | Enumerate direct, dependency, branch, error, business, and collection assertion candidates after producer discovery. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: assertion inventory | E1,E3 | MAPPED |
| IPM-AUTH-044 | Main 789–860, skipped-branch gate | Per property/scenario, write reachability and seed conflicts select Not exists, structural/omit, or normal ladder with nested-path proof. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: assertion gates | E1,E3 | MAPPED |
| IPM-AUTH-045 | Main 861–941, producer lock | Immutable hierarchical producer and execution rows bind assertions to operation, context, guard, payload, and order. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup producer/APB records | E1,E3 | MAPPED |
| IPM-AUTH-046 | Main 943–984, list uncertainty | Indexed/exact-count list assertions require terminal producer execution/order proof; safe fallback never removes a Scenario. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: list assertion decisions | E1,E3 | MAPPED |
| IPM-AUTH-047 | Main 986–998, assertion ladder | Use Verified → PredictedFromRules → Structural → Omitted; all outputs have trace support and RUF/concatenation values are mechanical. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup final assertion decisions | E1,E3 | MAPPED |
| IPM-AUTH-048 | Main 1002–1013, dependency-first | Crawl and author modes are mutually gated; active dependency work precedes authoring, downgrade, omission, or persistence. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: dependency workflow | E10 | MAPPED |
| IPM-AUTH-049 | Main 1015–1036, discovery | Known page-list helpers and Decision Table calls become concrete dependency rows before generic RUF handling. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: dependency extraction | E10 | MAPPED |
| IPM-AUTH-050 | Main 1038–1086, materialization | Every executable occurrence, property segment, RUF, DP, helper context, and Decision Table dependency is materialized and closed/terminal before use. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: RuleJSON scan | E1,E10 | MAPPED |
| IPM-AUTH-051 | Main 1088–1131, request planning | RuleCrawler payloads derive mechanically from READY rows with exact reference shapes, deduplication, retries, mappings, and pre-call gates. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: crawler request plan | E10 | MAPPED |
| IPM-AUTH-052 | Main 1132–1144, response transition | Match every response, scan fetched JSON immediately, advance context occurrence-locally, retain DP obligations, and continue while work is open. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: crawler response transition | E10 | MAPPED |
| IPM-AUTH-053 | Main 1146–1156, terminal gaps | LIMIT/KEYONLY/MISSING/OMIT_NONCRITICAL require exhausted factual evidence and cannot replace requestable work or support positive assertions. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: terminal dependency handling | E1,E10 | MAPPED |
| IPM-AUTH-054 | Main 1158–1165, caps | Explicit call/rule caps apply; remaining capacity plus READY work requires continued crawling; wave number is not a stop criterion. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: crawl limits | E10 | MAPPED |
| IPM-AUTH-055 | Main 1167–1219, examples | Preserve canonical continuation, context-separation, and helper-extraction examples as non-authoritative regression fixtures. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author crawler examples | E10 | MAPPED |
| IPM-AUTH-056 | Main 1221–1231, closure gates | Semantic closure precedes handoff; Generator separately owns projection, RuleCode, DP alignment, and candidate-write gates. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author handoff gate; Generator write gate | E2,E3,E5,E10 | MAPPED |
| IPM-AUTH-057 | Main 1233–1257, RUF | Critical RUFs require exact contracts, transitive closure, deterministic arguments, and explicit unknown-result gaps. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: RUF analysis | E1,E10 | MAPPED |
| IPM-AUTH-058 | Main 1259–1269, Decision Tables | Evaluate through DTM/DTA/DTE evidence; inactive scalar results create localized omissions while independent final effects remain traceable. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup Decision Table records | E1,E3,E10 | MAPPED |
| IPM-AUTH-059 | Main 1271–1285, property/context | Trace ordered RUT/dependency modifications, loops, indexes, contexts, and Decision Table effects; assert only final observable values. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup property execution traces | E1,E3 | MAPPED |
| IPM-AUTH-060 | Main 1287–1302, DP obligation | Every reachable/unknown DP signature becomes a concrete Scenario simulation obligation with exact parameters, seed context, output shape, and DPA alignment. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup simulation decisions | E1,E3,E6 | MAPPED |
| IPM-AUTH-061 | Main 1304–1333, seed depth | Simulation paths preserve exact RUT tokens and navigation depth; wrapper conventions cannot rename or deepen paths. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: simulation payload | E1,E3,E6 | MAPPED |
| IPM-AUTH-062 | Main 1335–1368, simulation scope | Only Thread-level Data Pages are simulated; excluded pages create gaps/downgrades and invalid scope returns to witness formation. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: simulation eligibility | E1,E3 | MAPPED |
| IPM-AUTH-063 | Main 1371–1380, simulation serialization | Scenario Author fixes DP mock semantics; Generator maps them to pySimulation with exact page/list and runtime seed shape. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup simulation contract; Generator projection | E3,E5,E6 | MAPPED |
| IPM-AUTH-064 | Main 1382–1383, seed coverage | Every seed-derived exact assertion has a matching physical seed; post-freeze changes require rematerialization or downgrade. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author: seed/assertion audit | E1,E3 | MAPPED |
| IPM-AUTH-065 | Main 1387–1415, property formatting | Property definitions govern structure, class, type, boolean form, and collection addressing. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author metadata; Generator fields | E1,E3,E5 | MAPPED |
| IPM-AUTH-066 | Main 1416–1423, Param assertions | Param assertions use exact Param paths and property assertion shape without page/real-name/parent-mode fields. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: parameter assertion projection | E5 | MAPPED |
| IPM-AUTH-067 | Main 1425–1437, regular assertions | Regular assertion page, class, relative target, and real name derive from immutable APB/runtime context. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author APB; Generator projection | E1,E3,E5 | MAPPED |
| IPM-AUTH-068 | Main 1439–1451, Page assertions | Page/list-item targets use Page assertions; Property assertions address scalar descendants only. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: assertion type projection | E5 | MAPPED |
| IPM-AUTH-069 | Main 1453–1472, comparators | Semantic assertion and property type determine comparator/value; booleans remain typed and never use existence semantics. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author decision; Generator field mapping | E1,E3,E5 | MAPPED |
| IPM-AUTH-070 | Main 1475–1493, Pega context | Preserve evidenced optional Pega context fields and valid compact Page forms unless forbidden or proven wrong. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: context preservation | E5,E8 | MAPPED |
| IPM-AUTH-071 | Main 1497–1515, cardinality | One physical group per non-When Scenario or distinct When simulation key; ordinary input/result differences do not split groups. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author groups; Generator entries | E3,E5,E6 | MAPPED |
| IPM-AUTH-072 | Main 1517–1530, compiler/grammar | One compiler owns census, witnesses, coverage, membership, freeze, IDs, typed data, escaping, and complete snapshot validation; replace only its MemoryTemp carrier. | STABLE | SCENARIO_AUTHOR | REPLACE | Versioned ScenarioGroup line-ledger | E1,E3,E4 | MAPPED |
| IPM-AUTH-073 | Main 1532–1538, INVENTORY | Census original-RUT behaviors only; dependencies never own targets; rule-type adapters govern Model, When, and original Decision Table coverage. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author INVENTORY phase | E1,E3 | MAPPED |
| IPM-AUTH-074 | Main 1539, WITNESSES | Build deterministic executable coverage witnesses, resolve all physical data/simulation, execute RUT, and merge only identical physical executions. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author WITNESSES phase | E1,E3,E6 | MAPPED |
| IPM-AUTH-075 | Main 1541, FROZEN | Reduce deterministically without coverage loss; re-execute/rebuild affected projections; assertions, confidence, and packaging cannot change frozen semantics. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author final semantic gate | E1,E3 | MAPPED |
| IPM-AUTH-076 | Main 1543–1545, B/A audit | Split current post-RuleCode recensus into Scenario Author pre-handoff semantic audit, Generator bijection audit, and Validator candidate audit. | CONFLICTING | SHARED_CONTRACT | REPLACE | Three role-specific audit gates | E1,E2,E3,E5,E7 | MAPPED |
| IPM-AUTH-077 | Main 1547–1550, nested DT setup | DTE/DTA setup is immutable before projection; Generator copies exact invocation-page setup and cannot add physical inputs. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup DTE/DTA data; Generator projection | E1,E3,E5 | MAPPED |
| IPM-AUTH-078 | Main 1552–1577, RuleCode allocation | Formal parameter type governs serialization; setup, P&C, cleanup, simulation, and expected-result fields have distinct uses. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: RuleCode construction | E3,E5 | MAPPED |
| IPM-AUTH-079 | Main 1579–1615, When structure | Each group has one Decision block, one Scenario per row, fixed cell order/shape, typed final Result, exact paths, and no simulated-DP input. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: MultInpComb projection | E5,E6 | MAPPED |
| IPM-AUTH-080 | Main 1617–1677, grouping key | Scenario Author computes locked full-simulation groups; Generator verifies and projects without semantic regrouping. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup key; Generator verification | E3,E6 | MAPPED |
| IPM-AUTH-081 | Main 1679–1708, synchronization | Only simulation differences split; Scenario, Decision row, traces, simulation, IDs, order, and narrative references remain locally synchronized. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup contract; Generator checks | E3,E6 | MAPPED |
| IPM-AUTH-082 | Main 1710–1730, DecisionResult | When Result requires terminal dependency evidence; critical gaps cannot be replaced by guesses or confidence downgrade. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup DecisionResult decision | E1,E3,E10 | MAPPED |
| IPM-AUTH-083 | Main 1732–1736, coverage/shape | Coverage comes only from compiler; full cells execute before freeze; rows share ordered columns and one final Result. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author cells/signature; Generator exact projection | E1,E3,E6 | MAPPED |
| IPM-AUTH-084 | Main 1738–1751, empty input | Empty input preserves initialized carrier/cell, omits only pyExpectedValue, uses EMPTY trace semantics, and is not Page non-existence. | STABLE | SHARED_CONTRACT | MOVE | ScenarioGroup cell contract; Generator serialization | E3,E6 | MAPPED |
| IPM-AUTH-085 | Main 1753–1784, input paths | Preserve namespace, leading dot, indexes, keys, spelling, casing, and locked root for primary-relative paths. | STABLE | SHARED_CONTRACT | MOVE | ScenarioGroup input-path contract; Generator projection | E3,E6 | MAPPED |
| IPM-AUTH-086 | Main 1786–1817, final row checks | Generator verifies exact group Scenario/row bijection, signature, cell order, Result, trace numbers, and paths before write. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: per-group projection validation | E5,E6 | MAPPED |
| IPM-AUTH-087 | Main 1819–1828, narratives | Narratives are at most two factual plain-language sentences matching seeded, checked, and simulated semantics. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup final narrative | E1,E3,E5 | MAPPED |
| IPM-AUTH-088 | Main 1832–1865, EvidenceSummary | Truthfully project closure, support, branches, simulation, complexity, counts, gaps, reasoning, and seed coverage from canonical evidence. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup evidence; Generator projection; Validator checks | E1,E3,E5,E7 | MAPPED |
| IPM-AUTH-089 | Main 1867–1886, MultInpComb trace | Each row has one trace per input and Result; paths, values, and local row indices match exact cells, including empty values. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup decisions; Generator formatting; Validator alignment | E3,E6,E7 | MAPPED |
| IPM-AUTH-090 | Main 1889–1967, trace grammar | Every final ASSERT/SIM/OMIT has one safely encoded grammar row; removed candidates become explicit omissions; support rules remain enforced. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup decision ledger; Generator format; Validator reconciliation | E3,E5,E7 | MAPPED |
| IPM-AUTH-091 | Main 1969–1984, structural/Param/SIM | Structural omission, Param shape, and DP SIM signature rules are exact and block projection when required evidence is absent. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author decisions; Generator projection; Validator checks | E3,E5,E7 | MAPPED |
| IPM-AUTH-092 | Main 1994–2010, confidence | Gaps deterministically cap confidence/testability; critical gaps force Low and partial/not-testable semantics. | STABLE | SCENARIO_AUTHOR | MOVE | ScenarioGroup confidence/testability | E1,E3 | MAPPED |
| IPM-AUTH-093 | Main 2011–2020, legacy loop | Replace Author persistence/validation/repair with Generator group reads, candidate writes, UUID validation, and projection-only repair. | CONFLICTING | UNIT_TEST_GENERATOR | REPLACE | Generator validation loop | E2,E4,E7,E9 | MAPPED |
| IPM-AUTH-094 | Main 2022–2057, write exceptions | Candidate write is single-attempt and terminal on detected failure; never validate or expose payload after failure. | LEGACY_TRANSPORT | UNIT_TEST_GENERATOR | REPLACE | Equivalent WriteMemory failure contract | E4,E7,E9 | MAPPED |
| IPM-AUTH-095 | Main 2059–2064, timing | Immutable ScenarioGroups finalize before Generator; every repaired projection gets a new candidate UUID without semantic mutation. | CONFLICTING | SHARED_CONTRACT | REPLACE | Handoff and repair-version contract | E3,E4,E7 | MAPPED |
| IPM-AUTH-096 | Main 2066–2093, regrouping | Generator projects one entry per supplied physical group and rejects invalid group contracts; it cannot merge/split immutable groups. | CONFLICTING | UNIT_TEST_GENERATOR | REPLACE | Generator: group projection/rejection | E2,E3,E6,E7 | MAPPED |
| IPM-AUTH-097 | Main 2095–2103, cell-trace gate | Preserve row/cell/trace bijection and exclude simulated DP roots; semantic cell defects become scoped rejection, not local deletion. | STABLE | SHARED_CONTRACT | SPLIT | Generator detection; semantic rejection report | E3,E6,E7 | MAPPED |
| IPM-AUTH-098 | Main 2105–2115, dependency evidence | Every unresolved dependency claim has canonical proof; active work returns to crawl and cannot support positive assertions. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author pre-handoff closure | E1,E3,E10 | MAPPED |
| IPM-AUTH-099 | Main 2116–2143, JSON checklist | Produce one parseable schema-guided root, synchronize RuleCode/evidence, preserve grouping/Param/simulation rules, and delegate strict validation. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: candidate checklist | E5,E6,E7 | MAPPED |
| IPM-AUTH-100 | Main 2144–2155, assertion/setup audit | Scenario Author resolves semantic ASSERT/OMIT; Generator detects mismatches but cannot remove or change semantic decisions. | CONFLICTING | SHARED_CONTRACT | SPLIT | Scenario Author decision gate; Generator rejection | E1,E3,E7 | MAPPED |
| IPM-AUTH-101 | Main 2156–2167, seed audit | Exclude forbidden seeds, preserve required DT before values, and rematerialize/re-execute on semantic conflict. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author final semantic audit | E1,E3 | MAPPED |
| IPM-AUTH-102 | Main 2168–2176, primary root | Root class/page/setup/P&C/context stay consistent; named pages require runtime-use evidence. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup root semantics; Generator metadata projection | E1,E3,E5,E7 | MAPPED |
| IPM-AUTH-103 | Main 2177–2183, target binding | Property assertion fields reconstruct mechanically from immutable APB, Scenario context, and root with full-path equality. | STABLE | UNIT_TEST_GENERATOR | MOVE | Generator: allowed projection repair | E3,E5,E7 | MAPPED |
| IPM-AUTH-104 | Main 2185–2200, DT integration | Resolve DTM/DTA/DTE consistency, inactive scalar omissions, final effects, and before values atomically without recomputing outcomes in Generator. | STABLE | SCENARIO_AUTHOR | MOVE | Scenario Author final DT audit | E1,E3,E7,E10 | MAPPED |
| IPM-AUTH-105 | Main 2202–2203, final memory gate | Complete audited semantic snapshots map exactly to physical groups before generation; use ordered immutable ScenarioGroup UUIDs. | LEGACY_TRANSPORT | SHARED_CONTRACT | REPLACE | Scenario Author WriteMemory handoff; Generator GetMemory | E3,E4,E6 | MAPPED |
| IPM-AUTH-106 | Main 2205–2219, references | Knowledge/RuleCrawler govern semantics, schema governs structure, examples are illustrative, and schema family follows immutable original RUTType. | STABLE | SHARED_CONTRACT | SPLIT | Scenario Author semantic authorities; Generator structural authorities | E2,E5,E6,E10 | MAPPED |

### Affected Validator inventory

| ID | Source | Stable behavior or invariant | Classification | Owner | Action | Target | Evidence | Status |
|---|---|---|---|---|---|---|---|---|
| IPM-VAL-001 | Validator 1–20, core contract | Validate an existing candidate, return only a compact report, never return corrected UnitTestRules, and emit no extra output. | STABLE | VALIDATOR | KEEP | Validator: core contract | E2,E7 | MAPPED |
| IPM-VAL-002 | Validator 5–7 | Replace CaseID/RUTType-only input with CaseID, immutable original RUTType, and current UnitTestCandidateUUID. | CONFLICTING | SHARED_CONTRACT | REPLACE | Generator/Validator interface | E4,E7 | MAPPED |
| IPM-VAL-003 | Validator 7,9–17 | Original RuleJSON type selects schema internally; caller-supplied schema is ignored. | STABLE | VALIDATOR | KEEP | Validator: schema selection | E5,E6,E7 | MAPPED |
| IPM-VAL-004 | Validator 22 | Preserve CaseID byte-for-byte; never add workpool class or normalize it. | STABLE | SHARED_CONTRACT | KEEP | Shared case identity contract | E4,E7 | MAPPED |
| IPM-VAL-005 | Validator 5, candidate persistence | Remove CaseID-only response-record addressing. | LEGACY_TRANSPORT | NONE | REMOVE | Superseded by DEC-002/003/007 Memory contract | E2,E4 | MAPPED |
| IPM-VAL-006 | Validator 24–30, tools | Replace legacy response read with exact GetMemory; retain schema validation and UTC documentation lookup; expose no write tool. | LEGACY_TRANSPORT | VALIDATOR | REPLACE | Validator tool allowlist | E2,E4,E7 | MAPPED |
| IPM-VAL-007 | Validator 31–51, KnowledgeTool | Use qualified composite keys; forbid bare/blank/double-underscore keys; MultInpComb keys are When-only. | STABLE | VALIDATOR | KEEP | Validator: KnowledgeTool contract | E5,E6,E10 | MAPPED |
| IPM-VAL-008 | Validator 51–57, UTC_KEYS | Retrieve KnowledgeArea, schema, and example once after schema success for both families; correct the current non-When omission. | CONFLICTING | VALIDATOR | REPLACE | Validator: complete UTC_KEYS | E5,E6,E10 | MAPPED |
| IPM-VAL-009 | Validator 60–124, report definition/output discipline | Preserve six-field compact ValidatorReport, fixed issue shape, issues-only defects/warnings, and raw JSON-only output. | STABLE | VALIDATOR | KEEP | Validator report contract | E7 | MAPPED |
| IPM-VAL-010 | Validator 80, routes | Replace Author routes with OK, GENERATOR_REPAIR, SEMANTIC_REJECT, HUMAN and deterministic precedence. | CONFLICTING | SHARED_CONTRACT | REPLACE | Validator/Generator route contract | E7 | MAPPED |
| IPM-VAL-011 | Validator 86–109, issue fields | Preserve code, severity, pointer, unit/scenario coordinates, decision ID, action, and message; define scenario/group/candidate scopes. | STABLE | SHARED_CONTRACT | SPLIT | Validator production; Generator consumption | E7 | MAPPED |
| IPM-VAL-012 | Validator 111–124 | Return exactly one compact raw report with no reasoning, wrappers, audit trail, success records, or prose. | STABLE | VALIDATOR | KEEP | Validator: output discipline | E7 | MAPPED |
| IPM-VAL-013 | Validator 126–136, execution order/input gate | Validate CaseID, immutable RUTType, and candidate UUID before all tool calls; derive schema before candidate inspection. | CONFLICTING | VALIDATOR | REPLACE | Validator: execution input gate | E4,E7 | MAPPED |
| IPM-VAL-014 | Validator 137–140 | Replace two-argument schema call with JsonValidationTool(CaseID, UUID, JsonSchema). | CONFLICTING | SHARED_CONTRACT | REPLACE | S1 tool and Validator call contract | E4,E5,E7 | MAPPED |
| IPM-VAL-015 | Validator 140–150 | Tool failure is distinct from schema-invalid JSON, stops later reads/checks, and routes HUMAN. | STABLE | VALIDATOR | KEEP | Validator: schema-tool failure | E7 | MAPPED |
| IPM-VAL-016 | Validator 153–178 | Copy schema result; short-circuit invalid candidates before Memory/documentation/semantic checks; classify failure deterministically. | STABLE | VALIDATOR | SPLIT | Validator schema handling; Generator repair route | E5,E7 | MAPPED |
| IPM-VAL-017 | Validator 158–178, mass failure | Preserve 25-error, broad-shape, and oversized-message compaction; Generator may rebuild projection from unchanged groups within the two-repair limit. | STABLE | SHARED_CONTRACT | SPLIT | Validator detection; Generator projection rebuild | E7 | MAPPED |
| IPM-VAL-018 | Validator 180–182 | After schema success, read only GetMemory(CaseID, UnitTestCandidate, UUID), never latest record. | LEGACY_TRANSPORT | VALIDATOR | REPLACE | Validator: candidate read | E4,E7 | MAPPED |
| IPM-VAL-019 | Validator 183–186, RUT metadata | Check immutable RUTType across every unit in the combined candidate and report exact unit scope; replace Author repair ownership. | CONFLICTING | VALIDATOR | REPLACE | Validator: all-unit metadata alignment | E6,E7 | MAPPED |
| IPM-VAL-020 | Validator 187–196, order | After schema/RUT checks, call KnowledgeTool once, then run trace/RuleCode and documentation checks. | STABLE | VALIDATOR | KEEP | Validator: execution order | E7,E10 | MAPPED |
| IPM-VAL-021 | Validator 198–204, source of truth | Schema tool alone decides strict validity; UTC docs govern RuleCode behavior; immutable semantic decisions govern candidate alignment. | STABLE | VALIDATOR | KEEP | Validator: source hierarchy | E5,E7 | MAPPED |
| IPM-VAL-022 | Validator 202–204, trace authority | Candidate trace is a trusted mechanical projection for Validator alignment; Generator alone proves it matches immutable ScenarioGroups and cannot create new semantics. | STABLE | SHARED_CONTRACT | SPLIT | ScenarioGroup authority; Generator bijection; Validator alignment | E3,E5,E7 | MAPPED |
| IPM-VAL-023 | Validator 206–227, trace format | Preserve ASSERT and MultInpComb DecisionInput/DecisionResult grammar and supports; SIM and OMIT grammar differences are replaced by IPM-VAL-043/044. | CONFLICTING | SHARED_CONTRACT | REPLACE | Canonical shared trace grammar | E3,E5,E6,E7 | MAPPED |
| IPM-VAL-024 | Validator 229–265, alignment checks | After schema success, compare normalized assertion/simulation/omission keys and decode trace entities plus one JSON-string layer. | STABLE | VALIDATOR | KEEP | Validator: normalized alignment | E7 | MAPPED |
| IPM-VAL-025 | Validator 267–284, paths | Never rewrite candidate; canonicalize paths/Param/duplicate segments; trace-only formatting repair may not alter semantics or correct RuleCode. | STABLE | SHARED_CONTRACT | SPLIT | Validator detection; Generator projection-only path repair | E7 | MAPPED |
| IPM-VAL-026 | Validator 286–298, MultInpComb alignment | Require exact row numbering, one trace per input/result cell, exact paths/values, and reject Result-only legacy trace. | STABLE | VALIDATOR | KEEP | Validator: decision alignment | E6,E7 | MAPPED |
| IPM-VAL-027 | Validator 301–311, bidirectional checks | Preserve ASSERT both ways, OMIT absence, SIM mapping, support, ResultCount/Param/DP shapes, and visible count consistency. | STABLE | VALIDATOR | KEEP | Validator: required alignment checks | E5,E7 | MAPPED |
| IPM-VAL-028 | Validator 313–316, empty input | Missing pyExpectedValue represents initialized empty value while retaining parent/cell symmetry. | STABLE | SHARED_CONTRACT | SPLIT | Scenario semantics; Generator row; Validator check | E3,E6,E7 | MAPPED |
| IPM-VAL-029 | Validator 319–332, semantic boundary | Check only explicit final decisions and visible contradictions; never infer assertions, values, simulations, dependencies, branches, or RUT behavior. | STABLE | VALIDATOR | KEEP | Validator: no-new-semantics boundary | E7 | MAPPED |
| IPM-VAL-030 | Validator 333, missing trace | Missing decision trace is SEMANTIC_REJECT, never Generator repair. | CONFLICTING | VALIDATOR | REPLACE | Validator: semantic rejection | E7 | MAPPED |
| IPM-VAL-031 | Validator 335–343, documentation validation | Documentation validation follows schema success, exact Memory read, and UTC lookup and is not a second schema validator. | STABLE | VALIDATOR | KEEP | Validator: documentation pass | E5,E7,E10 | MAPPED |
| IPM-VAL-032 | Validator 345–374, When checks | Preserve row count/signature/cell shape/order/Result, paths/labels, empty values, reserved-page ban, and no inferred true/false coverage; scope shared defects to group. | STABLE | SHARED_CONTRACT | SPLIT | Generator projection checks; Validator When checks/routes | E6,E7 | MAPPED |
| IPM-VAL-033 | Validator 376–386 | Never manually re-check JSON Schema keywords after the schema tool result. | STABLE | VALIDATOR | KEEP | Validator: schema boundary | E5,E7 | MAPPED |
| IPM-VAL-034 | Validator 388–390 | Missing IsInPageListWhen pxRuleReference is not blocking; visible contrary reasoning is SEMANTIC_REJECT. | STABLE | VALIDATOR | SPLIT | Validator: semantic contradiction route | E7,E10 | MAPPED |
| IPM-VAL-035 | Validator 392–405, Pega behavior | Preserve behavior checks for DP simulation, placement, page/list, Param/property assertions, comparators, errors, primary page, and P&C; unsafe ambiguity routes HUMAN. | STABLE | VALIDATOR | KEEP | Validator: documentation behavior | E5,E7 | MAPPED |
| IPM-VAL-036 | Validator 407–443, report construction | Replace obsolete Author-route examples while preserving exact compact report examples for OK, projection repair, semantic reject, and HUMAN. | CONFLICTING | VALIDATOR | REPLACE | Validator: report examples | E7 | MAPPED |
| IPM-VAL-037 | Validator 446–450, issue codes | Reconcile prose and embedded schema into one closed issue-code catalog. | CONFLICTING | VALIDATOR | REPLACE | Validator: issue-code catalog | E7 | MAPPED |
| IPM-VAL-038 | Validator 452–469, repair actions/routes | Encode projection-only Generator repair, semantic rejection, HUMAN escalation, and route precedence; remove Author-owned actions. | CONFLICTING | SHARED_CONTRACT | REPLACE | Validator report; Generator handler | E7 | MAPPED |
| IPM-VAL-039 | Validator 471–484, output lock | Keep one raw JSON report and name UnitTestGenerator, not Author, as the consumer. | CONFLICTING | VALIDATOR | REPLACE | Validator: output lock | E2,E7 | MAPPED |
| IPM-VAL-040 | Validator 487–657, report schema | Preserve closed Draft 2020-12 structure/coordinates while synchronizing route, code, and action enums with prose/examples. | CONFLICTING | VALIDATOR | REPLACE | Validator: embedded report schema | E5,E7 | MAPPED |
| IPM-VAL-041 | Validator 51,128–196,231,337, invocation limit | One invocation has one schema call, at most one exact Memory read, at most one UTC lookup, deterministic order, and no retry loop. | STABLE | VALIDATOR | KEEP | Validator: invocation completion gate | E7,E10 | MAPPED |
| IPM-VAL-042 | Validator 18,26–30,267,484, read-only | Validator never rewrites/writes candidates or persists validation/partial-failure records. | STABLE | VALIDATOR | KEEP | Validator: mutation prohibition | E2,E4,E7 | MAPPED |
| IPM-VAL-043 | Author 1921; Validator 222,237, SIM trace | Use the Author's complete canonical SIM grammar, including sig=DP_SIG and params=normalizedParams; Validator parses both and compares them with the exact pySimulation entry. | CONFLICTING | SHARED_CONTRACT | REPLACE | ScenarioGroup trace; Generator formatter; Validator SIM alignment | E3,E6,E7 | MAPPED |
| IPM-VAL-044 | Author 1952–1961,2190–2194; Validator 226–227, OMIT reasons | Use the Author's complete omission catalog, including inactive_evaluate_all_scalar and inactive_return_values_scalar, in ScenarioGroup grammar, Generator formatting, Validator trace parsing/alignment, and fixtures; do not add it to ValidatorReport schema. | CONFLICTING | SHARED_CONTRACT | REPLACE | Canonical shared OMIT catalog | E3,E7,E10 | MAPPED |

### Inventory reconciliation

- **Coverage:** Every normative Main and Validator heading/subheading and every identified cross-cutting hard lock in the declared inventory scope has at least one source anchor. Source ranges are semantic anchors, not a claim that blank lines or purely illustrative syntax are independently normative.
- **Counts:** 106 Author rows and 44 Validator rows; no stable row is unowned and no row removes stable behavior.
- **Conflict resolution:** All CONFLICTING rows map to replacements governed by DEC-001 through DEC-008, DEC-013 through DEC-014, and DEC-016. All LEGACY_TRANSPORT rows either replace legacy transport or remove only the obsolete response-record reference under DEC-002, DEC-003, and DEC-007.
- **Derived Validator rules:** The Validator aligns a mechanically projected candidate trace without reading source groups; Generator owns source-to-candidate bijection. Canonical SIM trace includes DP signature and normalized parameters, and the complete Author omission catalog is shared by all three agents. Mass schema failure permits projection rebuild from unchanged ScenarioGroups within the preserved two-repair limit. Trace-path repair is projection-only. Warning-only reports may remain valid with route OK. Schema-invalid precedence is tool failure → HUMAN, mass failure → GENERATOR_REPAIR, count mismatch → GENERATOR_REPAIR, ordinary invalid → GENERATOR_REPAIR.
- **Reverse trace:** `NOT_STARTED` because destination product prompts do not yet exist; S2–S4 must map every destination instruction back to these rows or an accepted new decision.
- **Independent coverage review:** `VERIFIED` — final read-only follow-up returned `PASS` with no findings on 2026-09-03.

## S1 Entry Contract Audit

- **Status:** `VERIFIED` by the mandatory independent S0 review and focused follow-up.
- **Outcome:** The accepted caller-facing contracts are sufficient to begin S1. DEC-019, accepted after S0 closure, assigns Pega tool implementation to the user and limits repository S1 work to call-contract design and static fixtures.

| Contract area | Fixed entry contract | Evidence | Repository S1 design and external implementation boundary |
|---|---|---|---|
| Write identity and immutability | `WriteMemory(CaseID, Type, Payload)` preserves CaseID, Type, and Payload; creates a new immutable record; generates and returns one opaque UUID; never updates an existing record. Automatic write retry is forbidden without an idempotency contract. | DEC-002, DEC-003, DEC-018; IPM-AUTH-011, 015, 023, 105 | S1 defines the caller-visible success/failure response and caller action. Ruleset, storage, UUID generation, and atomic implementation are external under DEC-019. |
| Exact read | `GetMemory(CaseID, Type, UUID)` requires all three address values, returns only the exact match and its unchanged Payload, and never falls back to a latest record. Callers pass CaseID and UUID unchanged. | DEC-002, DEC-003, DEC-018; IPM-VAL-004, 006, 018 | S1 defines exact response handling and not-found/address-mismatch behavior. Lookup and authorization implementation are external under DEC-019. |
| Payload boundary | Memory treats Payload as opaque. ScenarioGroup line-ledger grammar is owned by Scenario Author/Generator, while UnitTestCandidate JSON validity is owned by Generator/Validator; Memory parses neither. | DEC-005, DEC-018; IPM-AUTH-015, 105; IPM-VAL-022 | S1 supplies opaque-data call fixtures. Transport limits and Pega string/blob representation are external implementation details. |
| Supported types | v1 accepts exact Type values `ScenarioGroup` and `UnitTestCandidate`; readers validate Type as part of the address. | DEC-003 | S1 fixes caller literals and invalid-Type handling; enforcement implementation is external. |
| UUID-aware schema validation | `JsonValidationTool(CaseID, UUID, JsonSchema)` validates the exact `UnitTestCandidate` version addressed through Memory and returns boolean `IsValid` plus `ValidationMessage`; tool failure remains distinct from schema-invalid JSON. | DEC-007, DEC-018, DEC-019; IPM-VAL-014 through 018 | S1 defines caller branching and malformed-response handling. Internal lookup, Pega metadata, and schema-engine implementation are external. |
| Downstream orchestration boundary | Scenario Author writes ordered ScenarioGroup records; UnitTestGenerator reads their opaque UUIDs, writes new UnitTestCandidate versions after projection repair, and passes the current UUID to Validator. Validator is read-only and never selects a latest record. | DEC-001, DEC-004, DEC-006 through 008; IPM-AUTH-015, 023, 105; IPM-VAL-002, 006, 013, 018, 041, 042 | S1 specifies calls and traces; agent prompt/export implementation occurs in S2–S4; external tools are supplied by the user. |
| Failure and retry boundary | Missing/mismatched CaseID, Type, or UUID is a tool failure, never a substitute read. Failed writes return no usable UUID. Automatic write retry is forbidden; Validator has no retry loop. Repair attempts create new immutable candidate UUIDs. | DEC-002, DEC-006, DEC-007; IPM-VAL-015 through 018, 041 | S1 makes observable failure classes and deterministic caller actions explicit in static fixtures; Pega diagnostics and execution are external. |
| Artifact scope | S1 creates no Pega tool or backing artifact and instead designs caller contracts; S3 creates `UnitTestGenerator`; S4 completes Validator integration. `Main_Agent.txt` remains reference-only. | DEC-013, DEC-014, DEC-017, DEC-019 | Tool categories, backing rules, storage, exports, ChangeRequests, and runtime verification are user-owned and external. |

The external implementation details may not weaken exact addressing, immutability, opaque round-trip behavior, failure distinction, or no-retry rules. A later platform constraint that would weaken one of those invariants reopens S0 or requires a superseding accepted decision.

Allowed values:

- **Classification:** `STABLE`, `LEGACY_TRANSPORT`, `CONFLICTING`.
- **Destination owner:** `SCENARIO_AUTHOR`, `UNIT_TEST_GENERATOR`, `VALIDATOR`, `SHARED_CONTRACT`, or `NONE` only for accepted removal.
- **Migration action:** `KEEP`, `MOVE`, `SPLIT`, `REPLACE`, `REMOVE`.
- **Status:** `NOT_STARTED`, `MAPPED`, `IMPLEMENTED_NOT_VERIFIED`, `VERIFIED`, `BLOCKED`.

## Acceptance Criteria

- All five permitted continuity artifacts exist, use English, have valid internal references, and do not compete for operational state authority.
- `CONTINUITY.md` matches observed Git and repository state and contains exactly one next action.
- This ExecPlan contains exactly one next action and agrees with the S0 Roadmap entry.
- The Roadmap has one active stage and an acyclic dependency graph.
- Both schemas and examples parse as JSON after the standard example correction.
- Each example is validated against its matching schema. When no installed complete Draft 2020-12 or runnable Pega validator is available, two independent local implementations covering every assertion keyword used by the schemas satisfy S0, provided their results and the tooling limitation are recorded without claiming full-validator reproduction.
- `Main_Agent_Prompt.txt` has a recorded canonical hash/structure baseline, and the Validator prompt/export pair has recorded boundary and decoded-equivalence results.
- Accepted decisions map to Roadmap stages and expose no unresolved interface decision that blocks S1.
- The Instruction Preservation Matrix covers 100% of its inventory scope and every row has classification, owner, action, target, regression evidence, and status.
- No stable instruction is removed, orphaned, or assigned to conflicting owners; every accepted removal cites its decision and replacement or retirement evidence.
- Every completed high-risk action has a recorded independent subagent `PASS` report and root-agent reconciliation.
- An independent read-only validator returns a PASS result with no blocking findings.

## Validation

- Re-read all continuity artifacts after each material update.
- Use `git status`, branch inspection, and direct file inspection while the repository has no tracked baseline.
- Parse JSON using BOM-aware UTF-8 input.
- Use an already available Draft 2020-12 validator or the Pega JsonValidationTool when present; do not install a validator for this stage. When neither is available, validate every assertion keyword actually used with two independent local implementations and record the limitation.
- Record independent integrity evidence for `Main_Agent_Prompt.txt`. Compare only `Validator_Prompt.txt` with the decoded `<pySystemPrompt>` from `JsonValidator_tool.txt`, and inspect that export's boundaries and unrelated fields.
- Check Markdown links, Roadmap dependency cycles, active-stage count, exact-next-action count, evidence classifications, and decision-to-stage mapping.
- Verify complete forward matrix coverage in S0: every normative source item maps to a destination and regression evidence. As destination prompts are created in S2–S4, map each destination instruction back to source rows or an accepted new decision; perform the final complete reverse audit in S5.
- For each high-risk change, give a read-only subagent the changed files, relevant matrix rows, source baseline, acceptance criteria, and commands. Require scope, evidence, severity-ranked findings with file/line references, unverified checks, corrections, and a `PASS`, `FAIL`, or `BLOCKED` verdict.
- The root agent applies corrections and requests follow-up independent review when a blocking finding changes high-risk behavior; subagents never edit product or continuity files.
- Give an independent validator a read-only task covering all S0 acceptance criteria and record its evidence before closure.

### Prepared canonical-prompt and Validator-parity procedure

1. Record SHA-256 hashes, byte lengths, and logical-line counts for `Main_Agent_Prompt.txt`, `Validator_Prompt.txt`, and `JsonValidator_tool.txt`. Do not include or modify `Main_Agent.txt`.
2. Require exactly one opening and one closing `<pySystemPrompt>` tag in `JsonValidator_tool.txt`; extract only the bounded inner fragment with a single-line, non-greedy match.
3. Treat the extracted value as an HTML fragment, not as a standalone XML document. Convert `<br>` and block-closing tags to line boundaries, remove markup tags, decode named and numeric HTML entities, and normalize non-breaking spaces and line endings.
4. Normalize `Validator_Prompt.txt` with the same line-ending and non-breaking-space rules. Compare ordered non-empty logical lines after trimming trailing whitespace; preserve meaningful text, punctuation, code tokens, and list order.
5. Record the Main prompt baseline and the Validator normalized hashes, logical-line counts, equality result, and first differing source/export lines. If Validator equality fails, classify every difference before any edit; do not synchronize files during the validation step.
6. Confirm that the procedure is read-only, `Main_Agent.txt` is untouched, and no content outside the Validator `<pySystemPrompt>` changes.

## Evidence

- `VERIFIED` — `git rev-parse --show-toplevel` resolved the checkout root during S0 initialization; the machine-specific path is omitted under DEC-024 while preserving the historical observation.
- `VERIFIED` — branch inspection returned `main`; `git rev-parse --verify HEAD` failed because no commit exists.
- `VERIFIED` — `git status --short --branch` reported `No commits yet on main...origin/main [gone]` and 16 initial untracked files.
- `VERIFIED` — documentation discovery found only the pre-existing `AGENTS.md`.
- `FAILED` — BOM-aware JSON parsing of `rule-test-unit-case_JsonExample.txt` reported an illegal trailing comma at line 269, column 17.
- `VERIFIED` — both schemas and the MultInpComb example parsed with BOM-aware JSON reading.
- `VERIFIED` — all five continuity paths exist; Markdown links resolve; no competing state files exist; `AGENTS.md` contains 12 content lines and no detailed workflow body.
- `VERIFIED` — Roadmap dependencies are acyclic, all six stage IDs resolve, and `S0` is the only active stage.
- `VERIFIED` — `CONTINUITY.md` and this ExecPlan each contain one exact-next-action heading with identical action text.
- `VERIFIED` — the first seventeen accepted decisions contain every required field and reference only Roadmap stages `S0` through `S5`; DEC-018 has the same required structure and awaits independent review with the S1 entry-contract audit.
- `VERIFIED` — before the authorized JSON fix, all 15 product-file lengths matched the initial inventory and only the five continuity artifacts had been created or replaced. The standard example is now the only intentionally changed product artifact.
- `VERIFIED` — independent read-only audit of the preservation and high-risk-gate changes returned `PASS` with no findings on 2026-09-02; it confirmed explicit S2/S3 separation, the pre-edit matrix gate, root-only correction ownership, English-only scope, and unchanged product-file lengths.
- `VERIFIED` — the final independent matrix follow-up returned `PASS` on 2026-09-03 after the root agent corrected SIM-trace, OMIT-catalog, source-anchor, and destination-scope findings.
- `VERIFIED` — `rule-test-unit-case_JsonExample.txt` line 259 retains its required inter-item comma and line 269 no longer has the illegal trailing comma; SHA-256 is `D05A9EED430588DA8F9D7672E749352AE00D66AA7306663C254D67053AB0F446`; independent review returned `PASS`.
- `VERIFIED` — PowerShell, BOM-aware Python, and Node parsing passes for both schemas and examples; independent Python and Node validation of every used schema assertion keyword reports zero conformance errors. Python `jsonschema`, Node `ajv`, PowerShell `Test-Json`, and runnable Pega validation are unavailable, and no dependency was installed.
- `VERIFIED` — initial preparation found one `<pySystemPrompt>` boundary pair in each legacy export and undeclared `&nbsp;` entities prevent whole-export XML parsing. After user scope correction, only the Validator boundary/fragment participates in parity; `Main_Agent.txt` remains untouched reference evidence.
- `VERIFIED` — independent read-only scope review returned `PASS` on 2026-09-03 after generic S5 and S0 parity wording was limited to selected deliverable exports and `Main_Agent.txt` was explicitly excluded.
- `VERIFIED` — `Main_Agent_Prompt.txt` canonical baseline on 2026-09-03: SHA-256 `D6CDED6A4D786AC555452C05296B1A409042B5E6853B0FB9B9EC635AF065C290`; 177,990 bytes; 2,219 logical lines; 1,710 non-empty lines; 66 Markdown headings; six fence markers; CRLF line endings; no UTF-8 BOM.
- `VERIFIED` — raw Validator artifacts on 2026-09-03: `Validator_Prompt.txt` SHA-256 `F68E9362F7C85984552D806825BAA93F73B56762F158E91FC9E018F447474864`, 32,899 bytes, 657 logical lines, 519 non-empty lines; `JsonValidator_tool.txt` SHA-256 `779D7E65B8D3C473C111622070043D0327752A9EE12B3E14167587C632DEEE06`, 58,980 bytes, 309 logical lines, and exactly one opening and closing `<pySystemPrompt>` tag.
- `VERIFIED` — decoded Validator parity on 2026-09-03: both representations contain 519 ordered non-empty logical lines and share normalized SHA-256 `1B78FF5E6422BDE561A24704939D6185FCC7E70CF9806D76BBFBD55DB45B10AE`; their exact 3,137-token sequences share SHA-256 `EA7F8BEB5141599F07A32519B0F4905AB3318524F1DE6AE4A0EF89999387DBC0`. The first strict difference is logical line 7 and all 396 strict differences are HTML serializer-added leading spaces; no difference remains after trimming boundary whitespace. The check was read-only and did not inspect or modify `Main_Agent.txt`.
- `VERIFIED` — the 2026-09-03 S1 entry-contract audit maps every S1-facing invariant to accepted decisions and Instruction Preservation Matrix rows and records DEC-018 for the opaque Payload/UUID boundary; the independent final audit confirmed the caller-facing content is sufficient to begin S1. DEC-019 later moves Pega metadata and tool implementation outside repository scope while retaining response-envelope design as S1 caller-contract work.
- `FAILED` — the first final independent S0 audit on 2026-09-03 confirmed the S1/DEC-018 contract content and all reproduced technical evidence but found contradictory validator-fallback wording, a stale Roadmap conformance statement, and premature reverse-matrix scope; it required root correction and focused follow-up.
- `VERIFIED` — focused independent follow-up on 2026-09-03 found all three prior findings corrected, no new contradiction, disciplined classifications, valid links and stage mappings, unchanged product hashes, and no remaining blocking defect.
- `VERIFIED` — after S0 closure, the user-authorized initial baseline commit `99e038330076288bcc86bcc556681dc3efc82c74` (`chore: establish verified S0 baseline`) captured all 20 repository files before S1 was activated.

## Risks

- With no commit or tracked baseline, Git diff cannot prove the scope of early changes; use named-file inspection and recorded checks until a baseline is authorized.
- A syntax-only example fix may expose schema-conformance errors that require a separately justified change.
- Validator prompt/export equivalence may require normalization beyond entity decoding; record the method and avoid whole-export rewrites. Never introduce a `Main_Agent.txt` parity requirement without a new user decision.
- An incomplete instruction inventory can silently drop stable behavior during the split; product prompt changes are blocked until matrix coverage passes independent review.
- A validator subagent may miss a cross-file invariant if given incomplete scope; every high-risk review package must include source rows, destination rows, acceptance criteria, and relevant files.
- Missing externally implemented Pega tools can block later runtime integration even when repository caller contracts are complete; under DEC-019 they do not block S1 design closure.

## Exact Next Action

Follow `docs/execution/plans/S1-pega-memory-transport.md`; reopen S0 only if S1 discovery proves that a fixed S0 invariant cannot be implemented without a superseding decision.

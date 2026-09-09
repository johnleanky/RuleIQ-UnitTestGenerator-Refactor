"""ScenarioGroup 1.2 static consumer: validate source profiles, never infer them."""
from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path

import validate_s2_design as base

PROFILE_FIELDS = ("scenario", "id", "order", "data", "evidence")
PROFILE_KEYS = {"caseKey", "singlePage", "scenarioType", "actions", "bindings", "checklist", "reasoningTrace", "dependencyClosureTrace"}
CHECKLIST = {"CandidateAssertionsEnumerated", "DependencyResolutionCompleted", "RuleCrawlerLimitsApplied", "RUFTransitiveDiscoveryCompleted", "ParametersResolved", "BranchesEvaluated", "PropertyTracesCompleted", "OmissionsResolved", "ComplexityComputed", "SimulationNeedsResolved", "SimulationDepthChecked", "ListAssertionsChecked", "SymbolicIndexesResolved", "ContextSwitchesResolved", "UnsupportedAssertionsExcluded", "NoSpeculation", "NoInternalLedgerLeak"}
CONTEXT_FIELDS = {"pyCardApplyToClass", "pyPropertyApplyToClass", "pyStepPageNameActual", "pyStepPageMethodName", "pyListFilter", "pyNumberOfAppearances", "pyComparator"}
BINDING_KEYS = {"assertion", "structure", "scalarType", "stepPage", "stepClass", "fullPath", "parentMode", "context", "evidence"}
STRUCTURES = {"Value", "Page", "ValueList", "PageList", "ValueGroup", "PageGroup", "NotApplicable"}
SCALAR_TYPES = {"Text", "String", "Identifier", "Password", "TextEncrypted", "Integer", "Double", "Decimal", "Date", "DateTime", "TimeOfDay", "TrueFalse", "NotApplicable"}
ACTION_TYPES = {"ApplyDataTransform", "RunActivity", "LoadDataPage", "LoadObject", "CreateDataObject", "CreateWorkObject"}
RESERVED_ROOTS = {'pxProcess','AccessGroup','Application','OperatorID','Org','OrgDivision','pxRequestor','pxThread'}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def serialize(records):
    return ("\n".join(r["tag"] + "|" + "|".join(k + "=" + base.encode_value(v) for k, v in r["values"].items()) for r in records) + "\n").encode()


def parse_profile(line, number):
    base.require(not any(ord(c) < 32 for c in line), "PROFILE raw control")
    parts = base.split_record(line)
    fields = [part.split("=", 1) for part in parts[1:]]
    base.require(all(len(pair) == 2 for pair in fields) and tuple(pair[0] for pair in fields) == PROFILE_FIELDS, "PROFILE grammar")
    values = {k: base.decode_value(v) for k, v in fields}
    base.require(all(v is not None for v in values.values()), "PROFILE missing field")
    base.require(all(base.encode_value(values[k]) == v for k, v in fields), "PROFILE noncanonical encoding")
    return {"tag": "PROFILE", "line": number, "values": values}


def proof(evidence, references, kind, source, expected=None):
    """Select one acquisition snapshot; the final PROFILE census is never a source."""
    base.require(isinstance(references, list) and references and all(isinstance(e, str) and e in evidence for e in references), "PROFILE source references")
    matches = [evidence[e] for e in references if evidence[e]["kind"] == kind and evidence[e]["source"] == source]
    base.require(len(matches) == 1, "PROFILE source snapshot: " + source)
    value = base.canonical_json(matches[0]["fact"], "PROFILE source fact")
    if expected is not None:
        base.require(value == expected, "PROFILE source mismatch: " + source)
    return value


def action_sources(data, evidence, linked):
    identities = [{k: a[k] for k in ("phase", "type", "name", "page")} for a in data["actions"]]
    proof(evidence, linked, "EXECUTION", "EXECUTION_ACTIONS", identities)
    for index, action in enumerate(data["actions"]):
        proof(evidence, action["evidence"], "EXECUTION", "EXECUTION_ACTIONS", identities)
        resolved = [{k: p[k] for k in ("name", "valueType", "value")} for p in action["parameters"]]
        proof(evidence, linked, "EXECUTION", "ACTION_ARGUMENTS/" + str(index), resolved)
        for parameter in action["parameters"]:
            source = "ActionRule/" + action["type"] + "/" + action["name"] + "/pyParameters"
            declarations = proof(evidence, parameter["evidence"], "DEPENDENCY", source)
            base.require(isinstance(declarations, list), "PROFILE action declaration array")
            matches = [d for d in declarations if isinstance(d, dict) and d.get("pyParametersParamName") == parameter["name"]]
            base.require(len(matches) == 1 and matches[0].get("pyParametersParamType") == parameter["formalType"], "PROFILE unique action formal declaration")
            proof(evidence, parameter["evidence"], "EXECUTION", "ACTION_ARGUMENTS/" + str(index), resolved)


def trace_projection(rows, audit):
    """Render only recorded facts, retaining the original human-readable wave tokens."""
    closure = []
    for wave in audit["waves"]:
        n = wave["wave"]
        state = "; ".join(k + "=" + str(v) for k, v in wave["state"].items())
        plan = "; ".join(k + "=" + (",".join(v) if isinstance(v, list) else v) for k, v in wave["plan"].items())
        delta = "; ".join(k + "=" + (",".join(v) if isinstance(v, list) else v) for k, v in wave["delta"].items())
        closure.append(f"STATE W{n}: {state}. PLAN W{n}: {plan}. DELTA W{n}: {delta}.")
    if not closure:
        closure.append("No RuleCrawler waves occurred.")
    for r in rows:
        if r["tag"] == "DEP":
            d = r["values"]
            closure.append("D " + d["identity"] + ": state=" + d["state"] + "; proof=" + d["proof"] + ".")
    reasoning = " ".join(closure).replace("STATE W", "RCSTATE W").replace("PLAN W", "RCPLAN W")
    for r in rows:
        if r["tag"] in {"DTM", "DTE", "DTA", "DTC", "DTRA", "ASSERT", "OMIT"}:
            reasoning += " " + r["tag"] + " " + canonical({k: v for k, v in r["values"].items() if k not in {"scenario", "order", "evidence"}}) + "."
    for seed in audit["seeds"]:
        reasoning += " Seed " + seed["expression"] + " → " + seed["seedPath"] + " → asserts " + seed["assertionPath"] + "."
    return reasoning, " ".join(closure)


def validate_audit(rows, data, evidence, linked, crawl, revision="1.3"):
    audit = proof(evidence, linked, "EXECUTION", "EXECUTION_AUDIT")
    base.require(isinstance(audit, dict) and set(audit) == {"waves", "seeds"} and isinstance(audit["waves"], list) and isinstance(audit["seeds"], list), "PROFILE execution audit")
    summary = next(r["values"] for r in rows if r["tag"] == "SUMMARY")
    deps = {r["values"]["identity"]: r["values"] for r in rows if r["tag"] == "DEP" and r["values"]["identity"] is not None}
    base.require(len(audit["waves"]) == int(summary["maxDependencyWaveReached"]) <= int(crawl["ruleCrawlerCalls"]), "PROFILE actual wave census")
    for index, wave in enumerate(audit["waves"], 1):
        base.require(isinstance(wave, dict) and set(wave) == {"wave", "state", "plan", "delta"} and type(wave["wave"]) is int and wave["wave"] == index, "PROFILE wave identity")
        state, plan, delta = wave["state"], wave["plan"], wave["delta"]
        base.require(isinstance(state, dict) and set(state) == {"open", "ready", "ctx", "unscanned", "gaps"} and all(type(v) is int and v >= 0 for v in state.values()), "PROFILE wave state")
        base.require(isinstance(plan, dict) and set(plan) == {"OUT", "BLK", "ACT", "CHK"} and plan["CHK"] in {"PASS", "FIX"}, "PROFILE wave plan")
        base.require(isinstance(delta, dict) and set(delta) == {"returned", "new", "ready", "closed", "next"} and delta["next"] in {"CRAWL", "AUTHOR", "TERMINAL_BLOCKED"}, "PROFILE wave delta")
        for obj, keys in ((plan, ("OUT", "BLK", "ACT")), (delta, ("returned", "new", "ready", "closed"))):
            for key in keys:
                base.require(isinstance(obj[key], list) and all(isinstance(ref, str) and ref in deps for ref in obj[key]) and len(obj[key]) == len(set(obj[key])), "PROFILE wave dependency identity")
        base.require(set(delta["returned"]) <= set(plan["OUT"]) and all(deps[d]["state"] not in {"MISSING", "KEYONLY", "LIMIT"} for d in delta["returned"]), "PROFILE fetched RuleJSON outcome")
        base.require(all(deps[d]["state"] == "CLOSED" for d in delta["closed"]), "PROFILE closed dependency outcome")
        if index == len(audit["waves"]):
            base.require(len(delta["ready"]) == int(summary["queuedDependencyCount"]) and delta["next"] == ("AUTHOR" if summary["dependencyClosureStatus"] == "Closed" else "TERMINAL_BLOCKED"), "PROFILE final wave outcome")
    if revision == "1.4":
        base.require(sum(len(w["plan"]["OUT"]) for w in audit["waves"]) == int(crawl["dependencyReferencesRequested"]), "CRAWL requested-reference census")
    assertions = {r["values"]["id"]: r["values"] for r in rows if r["tag"] == "ASSERT"}
    seeds = {r["values"]["id"]: r for r in rows if r["tag"] in {"SETUP", "SIM"}}
    for seed in audit["seeds"]:
        base.require(isinstance(seed, dict) and set(seed) == {"source", "assertion", "expression", "seedPath", "assertionPath", "evidence"}, "PROFILE seed proof keys")
        base.require(seed["source"] in seeds and seed["assertion"] in assertions and all(isinstance(seed[k], str) and seed[k] for k in ("expression", "seedPath", "assertionPath")), "PROFILE seed proof references")
        src = seeds[seed["source"]]; a = assertions[seed["assertion"]]
        base.require(seed["assertionPath"] == a["target"], "PROFILE seed assertion path")
        prefix = "pySetupPages." + src["values"]["page"] + src["values"]["path"] if src["tag"] == "SETUP" else "pyPageDetails"
        base.require(seed["seedPath"] == prefix or (src["tag"] == "SIM" and seed["seedPath"].startswith(prefix + ".")), "PROFILE seed physical path")
        base.require(isinstance(seed["evidence"], list) and seed["evidence"] and all(e in evidence and evidence[e]["kind"] in {"SEED", "EXECUTION"} and evidence[e]["source"] not in {"SCENARIO_SNAPSHOT/PROFILE", "EXECUTION_AUDIT"} for e in seed["evidence"]), "PROFILE seed acquisition evidence")
    required_pairs = {(sid, aid) for sid, src in seeds.items() if src["tag"] == "SETUP" for aid, a in assertions.items() if a["target"] == src["values"]["path"] and a["support"] in {"Verified", "PredictedFromRules"}}
    base.require(required_pairs <= {(s["source"], s["assertion"]) for s in audit["seeds"]}, "PROFILE seed coverage proof missing")
    expected = trace_projection(rows, audit)
    base.require((data["reasoningTrace"], data["dependencyClosureTrace"]) == expected, "PROFILE cross-trace source mismatch")


def projection_provenance(records):
    """Revision 1.3 acquisition facts; no value-type or mock-page inference."""
    from decimal import Decimal, InvalidOperation
    result = {}
    for profile in [r['values'] for r in records if r['tag'] == 'PROFILE']:
        sid = profile['scenario']
        rows = [r['values'] for r in records if r['values'].get('scenario') == sid]
        evidence = {r['id']: r for r in rows if 'kind' in r and 'fact' in r}
        data = json.loads(profile['data']); expected_values = {}; bindings = {}; item_paths = {}
        for binding in data['bindings']:
            assertion = next(r['values'] for r in records if r['tag'] == 'ASSERT' and r['values']['scenario'] == sid and r['values']['id'] == binding['assertion'])
            fact = proof(evidence, binding['evidence'], 'EXECUTION', 'ASSERTION_VALUE/' + assertion['id'])
            base.require(isinstance(fact, dict) and set(fact) == {'valueType', 'value'} and fact['value'] == assertion['value'], 'ASSERT typed value provenance')
            kind, value = fact['valueType'], fact['value']
            base.require(isinstance(kind, str) and (value is None if kind == 'absent' else isinstance(value, str)), 'ASSERT typed carrier')
            if kind == 'number':
                try:
                    base.require(re.fullmatch(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?', value) is not None and Decimal(value).is_finite(), 'ASSERT finite number')
                except InvalidOperation as error: raise base.ContractError('ASSERT number') from error
            else: base.validate_typed(kind, value, 'ASSERT expected value')
            expected_values[assertion['id']] = fact
        for sim in [r['values'] for r in records if r['tag'] == 'SIM' and r['values']['scenario'] == sid]:
            fact = proof(evidence, base.ids(sim['evidence'], 'SIM evidence', False), 'EXECUTION', 'SIMULATION_BINDING/' + sim['id'])
            pages = json.loads(sim['setupPages'])
            base.require(isinstance(fact, dict) and set(fact) == {'payloadPage', 'itemPath'} and isinstance(fact['payloadPage'], str) and fact['payloadPage'], 'SIM payload page provenance')
            base.require((isinstance(fact['itemPath'], str) and fact['itemPath'].startswith('.')) if sim['shape'] == 'list' else fact['itemPath'] is None, 'SIM item collection provenance')
            base.require(pages and sum(p['pySetupPageName'] == fact['payloadPage'] for p in pages) == 1, 'SIM complete page census/binding')
            base.require(len({p['pySetupPageName'] for p in pages}) == len(pages), 'SIM unique page census')
            for page in pages:
                for seed in page['pyPageDetails']:
                    base.require(isinstance(seed['path'], str) and isinstance(seed['valueType'], str) and isinstance(seed['value'], str), 'SIM typed page-detail carrier')
                    base.validate_typed(seed['valueType'], seed['value'], 'SIM page-detail value')
            bindings[sim['id']] = fact['payloadPage']
            item_paths[sim['id']] = fact['itemPath']
        result[sid] = {'expectedValues': expected_values, 'simulationBindings': bindings, 'simulationItemPaths': item_paths}
    return result


def validate_carrier_roots(records):
    """Original Main20–24: reject physical top-level roots, not nested properties."""
    def page(name):
        if name is not None:
            base.require(re.split(r'[.(\s]',name.lstrip('.'))[0] not in RESERVED_ROOTS,'SOURCE_RESERVED_SYSTEM_PAGE')
    def absolute(path):
        if path is not None and not path.startswith('.'):page(path)
    root=records[1]['values'];page(root['page'])
    for name in json.loads(root['pagesAndClasses']):page(name)
    for named in json.loads(root['namedPageEvidence']):page(named['page'])
    for record in records:
        v=record['values'];tag=record['tag']
        if tag in {'INPUT','SETUP'}:
            page(v['page']);absolute(v['path'])
        elif tag=='COLUMN':absolute(v['path'])
        elif tag=='ASSERT' and v['kind']=='DecisionInput':absolute(v['target'])
        elif tag=='PARAM' and v['formalType']=='PAGE':page(v['value'])
        elif tag=='SIM':
            for carrier in json.loads(v['setupPages']):
                page(carrier['pySetupPageName'])
                for seed in carrier['pyPageDetails']:absolute(seed['path'])
        elif tag=='PROFILE':
            for action in json.loads(v['data'])['actions']:
                page(action['page'])
                for param in action['parameters']:
                    if param['formalType']=='PAGE':page(param['value'])


def read_ledger(path, revision='1.2'):
    raw = path.read_bytes()
    base.require(not raw.startswith(b"\xef\xbb\xbf") and raw.endswith(b"\n") and b"\r" not in raw, "profiled ledger raw framing")
    try:
        lines = raw.decode("utf-8")[:-1].split("\n")
    except UnicodeDecodeError as error:
        raise base.ContractError("profiled ledger invalid UTF-8") from error
    base.require(all(lines), "profiled ledger blank record")
    base.require(revision in {'1.2', '1.3', '1.4'} and lines[0].startswith('SG|version=' + revision + '|'), 'requires revision ' + revision + '; rematerialize source')
    records = []
    for number, line in enumerate(lines, 1):
        if line.startswith("PROFILE|"):
            records.append(parse_profile(line, number))
        else:
            records.append(base.parse_line(line, number, revision))
    # Reuse the reviewed common grammar/semantic core. This is a local validator
    # implementation detail, never a Memory rewrite or acceptance of legacy input.
    common = deepcopy([r for r in records if r["tag"] != "PROFILE"])
    common[0]["values"]["version"] = "1.1"
    if revision in {'1.3', '1.4'} and common[0]['values']['kind'] == 'WHEN' and common[0]['values']['simulationGroupKey'] != 'NO_SIMULATION':
        key = base.canonical_json(common[0]['values']['simulationGroupKey'], 'revision 1.3 key')
        base.require(isinstance(key, dict) and set(key) == {'simulations'} and isinstance(key['simulations'], list) and key['simulations'], 'revision 1.3 key root')
        for entry in key['simulations']:
            base.require(isinstance(entry, dict) and set(entry) == base.SIM_KEY_FIELDS | {'payloadPage', 'itemPath'}, 'revision 1.3 simulation key fields')
            del entry['payloadPage']
            del entry['itemPath']
        common[0]['values']['simulationGroupKey'] = canonical(key)
    validated = base.validate_ledger(base.MemoryFixture(path.name, serialize(common)), revision=revision)
    profiles = [r for r in records if r["tag"] == "PROFILE"]
    scenarios = [r["values"] for r in records if r["tag"] == "SCENARIO"]
    base.require([r["values"]["scenario"] for r in profiles] == [s["id"] for s in scenarios], "PROFILE scenario census/order")
    for profile in profiles:
        index = records.index(profile)
        scenario = profile["values"]["scenario"]
        prior = records[index - 1]
        base.require(prior["tag"] in {"SCENARIO", "NARRATIVE"}, "PROFILE position")
        base.require(records[index + 1]["values"].get("scenario") == scenario, "PROFILE body binding")
        base.require(profile["values"]["id"] == "F001" and profile["values"]["order"] == "1", "PROFILE identity/order")
        base.require(not any(r is not profile and r["values"].get("scenario") == scenario and r["values"].get("id") == "F001" for r in records), "PROFILE duplicate id")
    header = records[0]["values"]
    root = records[1]["values"]
    pages = json.loads(root["pagesAndClasses"])
    profile_map = {}
    for profile in profiles:
        scenario = profile["values"]["scenario"]
        rows = [r for r in records if r["values"].get("scenario") == scenario and r["tag"] != "PROFILE"]
        evidence = {r["values"]["id"]: r["values"] for r in rows if r["tag"] == "EVIDENCE"}
        data = base.canonical_json(profile["values"]["data"], "PROFILE data")
        base.require(isinstance(data, dict) and set(data) == PROFILE_KEYS, "PROFILE data keys")
        linked = base.ids(profile["values"]["evidence"], "PROFILE evidence", False)
        base.require(all(e in evidence for e in linked), "PROFILE evidence reference")
        base.require(any(evidence[e]["kind"] == "GATE" and evidence[e]["source"] == "SCENARIO_SNAPSHOT/PROFILE" and evidence[e]["fact"] == canonical(data) for e in linked), "PROFILE frozen census evidence")
        case_key = data["caseKey"]
        base.require(isinstance(case_key, str), "PROFILE case key type")
        key_parts = case_key.split()
        base.require(len(key_parts) >= 3 and key_parts[:3] == [header[k].upper() for k in ("rutType", "rutClass", "rutName")], "PROFILE case/RUT identity")
        base.require(any(evidence[e]["kind"] == "RUT" and evidence[e]["source"] == "GetCaseData/TestedRuleKey" and evidence[e]["fact"] == canonical({"TestedRuleKey": case_key}) for e in linked), "PROFILE case key provenance")
        base.require(data["singlePage"] in {"true", "false", None}, "PROFILE single-page value")
        if header["rutType"] in {"Rule-Obj-Model", "Rule-Obj-When"}:
            base.require(data["singlePage"] == "false", "PROFILE fixed single-page mode")
        elif data["singlePage"] is not None:
            base.require(any(evidence[e]["kind"] == "RUT" and evidence[e]["source"] == "RuleJSON/pyIsSinglePageImplementation" and evidence[e]["fact"] == canonical({"pyIsSinglePageImplementation": data["singlePage"]}) for e in linked), "PROFILE single-page provenance")
        else:
            gaps = [r["values"] for r in rows if r["tag"] == "GAP"]
            meta = next(s for s in scenarios if s["id"] == scenario)
            base.require(any(g["code"] == "RUT_EXECUTION_MODE_UNAVAILABLE" for g in gaps) and meta["testability"] != "Testable", "PROFILE unavailable execution mode lacks GAP")
        base.require(data["scenarioType"] in {"Baseline", "Edge"}, "PROFILE scenario type")
        base.require(isinstance(data["checklist"], dict) and set(data["checklist"]) == (CHECKLIST - {"ComplexityComputed"} if revision == "1.4" else CHECKLIST) and all(type(v) is bool for v in data["checklist"].values()), "PROFILE checklist")
        if not all(data["checklist"].values()):
            meta = next(s for s in scenarios if s["id"] == scenario)
            base.require(any(r["tag"] == "GAP" for r in rows) and meta["testability"] != "Testable" and meta["confidence"] != "High", "PROFILE false gate without downgrade")
        for field in ("reasoningTrace", "dependencyClosureTrace"):
            base.require(isinstance(data[field], str) and data[field].strip(), "PROFILE factual trace")
        base.require(isinstance(data["bindings"], list) and all(isinstance(b, dict) for b in data["bindings"]), "PROFILE bindings object array")
        assertions = [r["values"] for r in rows if r["tag"] == "ASSERT" and r["values"]["kind"] not in {"DecisionInput", "DecisionResult"}]
        base.require([b.get("assertion") for b in data["bindings"]] == [a["id"] for a in assertions], "PROFILE ASSERT binding census")
        for binding, assertion in zip(data["bindings"], assertions):
            base.require(set(binding) == BINDING_KEYS, "PROFILE binding keys")
            base.require(binding["structure"] in STRUCTURES and binding["scalarType"] in SCALAR_TYPES, "PROFILE property metadata")
            parent = binding["parentMode"]
            base.require(parent is None or parent in {"ValueList", "PageList", "ValueGroup", "PageGroup"}, "PROFILE parent mode")
            base.require(binding["stepPage"] in pages and pages[binding["stepPage"]] == binding["stepClass"], "PROFILE step page/class")
            target = assertion["target"]
            expected_full = target if target.startswith("Param.") or not target.startswith(".") else assertion["page"] + target
            base.require(binding["fullPath"] == expected_full, "PROFILE full target")
            if target.startswith("Param."):
                base.require(assertion["kind"] == "Property" and assertion["mode"] == "Text" and parent is None, "PROFILE Param assertion shape")
            else:
                base.require(expected_full.startswith(binding["stepPage"] + "."), "PROFILE relative assertion target")
            base.require(not (assertion["kind"] == "Property" and binding["structure"] in {"Page", "PageList", "PageGroup"}), "PROFILE page target as Property")
            if assertion["kind"] == "Property" and not target.startswith("Param."):
                base.require(binding["scalarType"] == assertion["mode"], "PROFILE scalar type drift")
                base.require(parent == (binding["structure"] if binding["structure"] in {"ValueList", "ValueGroup"} else None), "PROFILE collection parent mode")
            context = binding["context"]
            base.require(isinstance(context, dict) and set(context) <= CONTEXT_FIELDS and all(isinstance(v, str) and v for v in context.values()), "PROFILE optional context")
            base.require("pyNumberOfAppearances" not in context or (assertion["kind"] == "List" and context["pyNumberOfAppearances"] in {"InAllInstances", "InAnyInstance"}), "PROFILE List appearance semantics")
            base.require("pyListFilter" not in context or assertion["kind"] in {"List", "ResultCount"}, "PROFILE filter context")
            base.require("pyComparator" not in context or (assertion["kind"] == "Page" and context["pyComparator"] == assertion["comparator"]), "PROFILE Page comparator context")
            base.require(isinstance(binding["evidence"], list) and binding["evidence"] and all(e in evidence for e in binding["evidence"]), "PROFILE binding evidence")
            proof(evidence, binding["evidence"], "DEPENDENCY", "PROPERTY_DEFINITION/" + assertion["id"], {"path": binding["fullPath"], "pyPropertyMode": binding["structure"], "pyStringType": binding["scalarType"]})
            ctx = proof(evidence, binding["evidence"], "EXECUTION", "ASSERTION_CONTEXT/" + assertion["id"])
            expected_ctx = {k: binding[k] for k in ("stepPage", "stepClass", "fullPath", "parentMode", "context")}
            base.require(isinstance(ctx, dict) and set(ctx) == set(expected_ctx) | {"producerIndex", "payloadProven"} and all(ctx[k] == v for k, v in expected_ctx.items()) and ctx["producerIndex"] in {"Known", "Unknown", "NotApplicable"} and type(ctx["payloadProven"]) is bool, "PROFILE assertion context source")
            if assertion["kind"] == "List" and ctx["producerIndex"] == "Unknown":
                base.require(ctx["payloadProven"] and context.get("pyNumberOfAppearances") == "InAnyInstance", "PROFILE unknown index requires proven InAnyInstance")
        base.require(isinstance(data["actions"], list), "PROFILE actions array")
        phase_order = []
        for action in data["actions"]:
            base.require(isinstance(action, dict) and set(action) == {"phase", "type", "name", "page", "parameters", "evidence"}, "PROFILE action keys")
            base.require(action["phase"] in {"SETUP", "CLEANUP"} and action["type"] in ACTION_TYPES and isinstance(action["name"], str) and action["name"], "PROFILE action identity")
            phase_order.append(0 if action["phase"] == "SETUP" else 1)
            base.require(action["page"] is None or action["page"] in pages, "PROFILE action page")
            base.require(isinstance(action["evidence"], list) and action["evidence"] and all(e in evidence for e in action["evidence"]), "PROFILE action evidence")
            simulated = {r["values"]["rule"] for r in rows if r["tag"] == "SIM"}
            base.require(not (action["type"] == "LoadDataPage" and action["name"] in simulated), "PROFILE simulation represented as action")
            base.require(isinstance(action["parameters"], list), "PROFILE action parameters")
            names = []
            for parameter in action["parameters"]:
                base.require(isinstance(parameter, dict) and set(parameter) == {"name", "formalType", "valueType", "value", "evidence"}, "PROFILE action parameter keys")
                base.require(isinstance(parameter["name"], str) and parameter["name"], "PROFILE action parameter name")
                names.append(parameter["name"])
                base.require(isinstance(parameter["formalType"], str) and isinstance(parameter["valueType"], str) and (parameter["value"] is None if parameter["valueType"] == "absent" else isinstance(parameter["value"], str)), "PROFILE action value carrier")
                base.validate_typed(parameter["valueType"], parameter["value"], "PROFILE action parameter")
                base.require(base.project_rut_parameter_value(parameter["formalType"], parameter["valueType"], parameter["value"], pages) is not None, "PROFILE unprojectable action parameter")
                base.require(isinstance(parameter["evidence"], list) and parameter["evidence"] and all(e in evidence for e in parameter["evidence"]), "PROFILE action parameter evidence")
            base.require(len(names) == len(set(names)), "PROFILE duplicate action parameter")
        base.require(phase_order == sorted(phase_order), "PROFILE action phase order")
        action_sources(data, evidence, linked)
        validate_audit(rows, data, evidence, linked, next(r["values"] for r in records if r["tag"] == ("CRAWL" if revision == "1.4" else "COMPLEXITY")), revision)
        profile_map[scenario] = data
    base.require(len({(p["caseKey"], p["singlePage"]) for p in profile_map.values()}) == 1, "PROFILE shared RUT metadata")
    validated.update(records=records, profiles=profile_map, raw=raw)
    if revision in {'1.3', '1.4'}:
        validate_carrier_roots(records)
        projected = projection_provenance(records)
        if header['kind'] == 'WHEN' and header['simulationGroupKey'] != 'NO_SIMULATION':
            key = json.loads(header['simulationGroupKey'])['simulations']
            for sid, facts in projected.items():
                sims = [r['values'] for r in records if r['tag'] == 'SIM' and r['values']['scenario'] == sid]
                base.require([e['payloadPage'] for e in key] == [facts['simulationBindings'][s['id']] for s in sims], 'SIM binding group key mismatch')
                base.require([e['itemPath'] for e in key] == [facts['simulationItemPaths'][s['id']] for s in sims], 'SIM item-path group key mismatch')
        for sid, facts in projected.items(): profile_map[sid].update(facts)
    if revision == "1.4":
        from dp_parameters import validate
        validate(records)
    return validated

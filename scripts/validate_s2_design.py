#!/usr/bin/env python3
"""Deterministic repository-static validation for the S2 design-freeze package."""

from __future__ import annotations

import json
import hashlib
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "s2"
SLICE = ROOT / "docs" / "execution" / "design" / "S2-instruction-implementation-slice.md"
S0_PLAN = ROOT / "docs" / "execution" / "plans" / "S0-baseline-contracts.md"
PROMPT = ROOT / "Main_Agent_Prompt.txt"
SCENARIO_CONTRACT = ROOT / "docs" / "contracts" / "SCENARIO_GROUP_V1.md"

ID_RE = re.compile(r"^[A-Za-z0-9._:-]+$")
IPM_RE = re.compile(r"^IPM-AUTH-(\d{3})$")
REGRESSION_RE = re.compile(r"^S2-R(\d{3})$")
BATCH1_IDS = {f"IPM-AUTH-{number:03d}" for number in (*range(1, 21), *range(27, 33))}
BATCH2_IDS = {f"IPM-AUTH-{number:03d}" for number in (*range(21, 27), *range(33, 93))}
BATCH3_IDS = {f"IPM-AUTH-{number:03d}" for number in range(93, 107)}
# Fixed reviewed content, canonicalized to LF only for repository regression.
# ScenarioGroup payload encoding and opaque Memory transport are unaffected.
S2_BASELINE_PROMPT_SHA256 = "6F059B641B9CF8B627E6879ED5B7A8FAEE78A616E71E2DD305AF8C051ACD215F"
PROFILE_BASELINE_SHA256 = "D1D790346AB759DF3EFE0BF02377C7E7A789C7FCDEC22938775A835812BAC036"
PROJECTION_BASELINE_SHA256 = "1D80FE31995009F062D1EA5AE5F843187EA050A366A443E5CDB70CF773F352CC"
FINAL_PROMPT_SHA256 = "1DD54CB6ABB8BE12C6092A1DF3B5CDEC46E383EE709C752694A798DE2A2456ED"
FINAL_CRLF_PROMPT_SHA256 = "DE6D9E6B8F07D62CD52AFA1FA73AF0F9A3980CC4BACC4CC08248A7FAA86B2C00"
FINAL_PROMPT_LINE_COUNT = 2029
PROFILE_IDS = {"IPM-AUTH-046", "IPM-AUTH-065", "IPM-AUTH-067", "IPM-AUTH-070", "IPM-AUTH-078", "IPM-AUTH-088", "IPM-AUTH-105"}
FORMAL_PROVENANCE_IDS = {"IPM-AUTH-035", "IPM-AUTH-072", "IPM-AUTH-078", "IPM-AUTH-105"}

FIELDS = {
    "SG": ("version", "caseId", "rutType", "rutClass", "rutName", "ruleset", "groupId", "groupOrder", "kind", "scenarioCount", "simulationGroupKey"),
    "ROOT": ("page", "class", "primarySetup", "pagesAndClasses", "namedPageEvidence"),
    "TARGET": ("id", "order", "source", "behavior", "constraint", "state", "proof"),
    "COLUMN": ("id", "order", "path", "class", "mode", "source", "simulatedRoot"),
    "CRAWL": ("ruleCrawlerCalls", "dependencyReferencesRequested", "triggeredLimits"),
    "COMPLEXITY": ("invocationCount", "whenRuleReferenceCount", "maxNesting", "operationCount", "loopCount", "modifiedPropertyCount", "conditionalBlockCount", "pageParameterCount", "unresolvedCriticalDependencyCount", "invocationChainDepth", "weightedScore", "tier", "ruleCrawlerCalls", "dependencyReferencesRequested", "hardTriggers", "triggeredLimits", "confidenceCap", "testabilityCap"),
    "SCENARIO": ("id", "order", "name", "owner", "covers", "testability", "confidence"),
    "PARAM": ("scenario", "id", "order", "invocation", "dependency", "name", "formalType", "formalEvidence", "mode", "inheritance", "expression", "valueType", "value", "evidence"),
    "INPUT": ("scenario", "id", "order", "role", "path", "page", "class", "mode", "valueType", "value", "resolution", "evidence"),
    "SETUP": ("scenario", "id", "order", "role", "path", "page", "class", "mode", "valueType", "value", "evidence"),
    "RX": ("scenario", "id", "order", "source", "operation", "context", "guard", "inputs", "result", "writes", "evidence"),
    "DEP": ("scenario", "id", "order", "kind", "identity", "state", "parameters", "proof", "evidence"),
    "BRANCH": ("scenario", "id", "order", "source", "logic", "inputs", "result", "writes", "evidence"),
    "PRODUCER": ("scenario", "id", "order", "target", "operation", "context", "guard", "payload", "execution", "evidence"),
    "PROPERTY": ("scenario", "id", "order", "target", "support", "deterministic", "valueType", "value", "producers", "evidence"),
    "DTM": ("scenario", "id", "order", "source", "mode", "scalarEnabled", "evidence"),
    "DTE": ("scenario", "id", "order", "dtm", "status", "scalarState", "scalarType", "scalarValue", "actions", "consumers", "evidence"),
    "DTA": ("scenario", "id", "order", "dte", "target", "page", "class", "operation", "beforeType", "before", "afterType", "after", "status", "evidence"),
    "DTC": ("scenario", "id", "order", "dte", "target", "decision", "evidence"),
    "DTRA": ("scenario", "id", "order", "dte", "source", "removedScalar", "checkedActions", "omitted", "pass", "evidence"),
    "SIM": ("id", "rule", "sig", "shape", "method", "class", "itemClass", "params", "target", "mockingRuleType", "referredFromClass", "setupPages", "scenario", "order", "payload", "parameterResolutions", "evidence"),
    "ASSERT_STD": ("id", "kind", "target", "page", "class", "mode", "comparator", "value", "support", "scenario", "order", "producer", "evidence"),
    "ASSERT_DEC": ("id", "kind", "row", "target", "page", "class", "mode", "comparator", "value", "support", "scenario", "order", "producer", "evidence"),
    "OMIT": ("id", "target", "reason", "scenario", "order", "evidence"),
    "EVIDENCE": ("scenario", "id", "order", "kind", "source", "fact", "support", "confidence"),
    "GAP": ("scenario", "id", "order", "dependency", "code", "scope", "effect", "evidence"),
    "SUMMARY": ("scenario", "id", "order", "supportLevel", "dependencyState", "branchState", "simulationState", "complexityTier", "assertionCount", "omissionCount", "simulationCount", "gapCount", "internalChecklist", "reasoningEvidence", "dependencyEvidence", "blockingGaps", "dependencyClosureStatus", "maxDependencyWaveReached", "queuedDependencyCount", "unscannedFetchedRuleJsonCount", "seedCoverageEvidence"),
    "NARRATIVE": ("scenario", "id", "order", "text", "evidence"),
    "END": ("targetCount", "columnCount", "paramCount", "scenarioCount", "inputCount", "setupCount", "rxCount", "depCount", "branchCount", "producerCount", "propertyCount", "dtCount", "simCount", "assertCount", "omitCount", "evidenceCount", "gapCount", "summaryCount", "narrativeCount", "complete"),
}

BODY_ORDER = {
    tag: index
    for index, tag in enumerate(
        ("PARAM", "INPUT", "SETUP", "RX", "DEP", "BRANCH", "PRODUCER", "PROPERTY", "DTM", "DTE", "DTA", "DTC", "DTRA", "SIM", "ASSERT", "OMIT", "EVIDENCE", "GAP", "SUMMARY", "NARRATIVE")
    )
}

NULLABLE = {
    "SG": {"simulationGroupKey"},
    "TARGET": {"constraint", "proof"},
    "PARAM": {"formalType", "formalEvidence", "expression", "value"},
    "INPUT": {"page", "class", "resolution"},
    "RX": {"guard", "inputs", "writes"},
    "DEP": {"parameters"},
    "BRANCH": {"inputs", "writes"},
    "PRODUCER": {"guard"},
    "PROPERTY": {"value", "producers"},
    "DTE": {"scalarValue", "actions", "consumers"},
    "DTA": {"before", "after"},
    "DTRA": {"removedScalar", "checkedActions", "omitted"},
    "SIM": {"itemClass", "referredFromClass"},
    "ASSERT_STD": {"page", "value", "producer"},
    "ASSERT_DEC": {"producer"},
    "GAP": {"dependency"},
    "SUMMARY": {"dependencyEvidence", "blockingGaps", "seedCoverageEvidence"},
    "CRAWL": {"triggeredLimits"},
    "COMPLEXITY": {"hardTriggers", "triggeredLimits"},
}

OMIT_REASONS = {
    "unresolved_external_source",
    "unavailable_rulejson_after_limit_exhaustion",
    "unresolvable_runtime_input",
    "inactive_evaluate_all_scalar",
    "inactive_return_values_scalar",
    "schema_incompatible_assertion_target",
    "redundant_iteration_coverage",
    "incorrect_candidate_assertion",
}

TRACE_FIELDS = {
    "SIM": ("id", "rule", "sig", "shape", "method", "class", "itemClass", "params", "target"),
    "ASSERT_STD": ("id", "kind", "target", "page", "class", "mode", "comparator", "value", "support"),
    "ASSERT_DEC": ("id", "kind", "row", "target", "page", "class", "mode", "comparator", "value", "support"),
    "OMIT": ("id", "target", "reason"),
}


class ContractError(ValueError):
    pass


class MemoryFixture:
    def __init__(self, name: str, payload: bytes):
        self.name = name
        self.payload = payload

    def read_bytes(self) -> bytes:
        return self.payload


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def split_record(line: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    index = 0
    while index < len(line):
        char = line[index]
        if char == "\\":
            require(index + 1 < len(line), "dangling escape")
            current.extend((char, line[index + 1]))
            index += 2
        elif char == "|":
            parts.append("".join(current))
            current = []
            index += 1
        else:
            current.append(char)
            index += 1
    parts.append("".join(current))
    return parts


def decode_value(raw: str):
    if raw == "-":
        return None
    if raw == r"\0":
        return ""
    output: list[str] = []
    index = 0
    escapes = {"\\": "\\", "|": "|", "r": "\r", "n": "\n", "t": "\t", "-": "-"}
    while index < len(raw):
        if raw[index] != "\\":
            output.append(raw[index])
            index += 1
            continue
        require(index + 1 < len(raw), "dangling value escape")
        code = raw[index + 1]
        require(code in escapes and code != "0", f"unknown value escape \\{code}")
        output.append(escapes[code])
        index += 2
    return "".join(output)


def encode_value(value) -> str:
    if value is None:
        return "-"
    if value == "":
        return r"\0"
    if value == "-":
        return r"\-"
    escapes = {"\\": r"\\", "|": r"\|", "\r": r"\r", "\n": r"\n", "\t": r"\t"}
    return "".join(escapes.get(char, char) for char in value)


def parse_line(line: str, line_number: int, revision="1.1") -> dict:
    require(not any(ord(char) < 32 for char in line), f"line {line_number}: raw control character")
    parts = split_record(line)
    tag = parts[0]
    require(tag in FIELDS or tag == "ASSERT", f"line {line_number}: unknown tag {tag}")
    pairs = []
    for item in parts[1:]:
        require("=" in item, f"line {line_number}: missing '='")
        key, raw = item.split("=", 1)
        require(re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", key) is not None, f"line {line_number}: invalid key {key}")
        decoded = decode_value(raw)
        require(encode_value(decoded) == raw, f"line {line_number}: non-canonical value encoding for {key}")
        pairs.append((key, raw, decoded))
    values = {key: value for key, _, value in pairs}
    require(len(values) == len(pairs), f"line {line_number}: duplicate field")
    schema_key = tag
    if tag == "ASSERT":
        schema_key = "ASSERT_DEC" if values.get("kind") in {"DecisionInput", "DecisionResult"} else "ASSERT_STD"
    require(tag != "COMPLEXITY" or revision != "1.4", "obsolete COMPLEXITY record")
    fields = FIELDS[schema_key]
    if revision == "1.4" and tag == "SUMMARY": fields = tuple(k for k in fields if k != "complexityTier")
    require(tag != "CRAWL" or revision == "1.4", "CRAWL requires revision 1.4")
    require(tuple(key for key, _, _ in pairs) == fields, f"line {line_number}: field order/arity mismatch for {tag}")
    nullable = NULLABLE.get(schema_key, set())
    if revision == "1.4" and tag == "SIM": nullable = nullable | {"parameterResolutions"}
    require(all(value is not None or key in nullable for key, value in values.items()), f"line {line_number}: non-null field uses absent token")
    return {"tag": tag, "line": line_number, "values": values, "raw": {key: raw for key, raw, _ in pairs}}


def integer(record: dict, key: str) -> int:
    value = record["values"][key]
    require(value is not None and re.fullmatch(r"0|[1-9][0-9]*", value) is not None, f"line {record['line']}: {key} is not an integer")
    return int(value)


def canonical_json(value, context: str):
    require(value is not None, f"{context}: JSON cannot be absent")
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise ContractError(f"{context}: invalid JSON: {error}") from error
    canonical = json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    require(value == canonical, f"{context}: JSON is not canonical")
    return parsed


def ids(value, context: str, allow_absent: bool = True) -> list[str]:
    if value is None:
        require(allow_absent, f"{context}: absent ID set")
        return []
    result = value.split(",")
    require(all(ID_RE.fullmatch(item) for item in result), f"{context}: invalid ID set")
    require(result == sorted(set(result)), f"{context}: IDs must be unique and sorted")
    return result


def sorted_tokens(value, context: str) -> list[str]:
    if value is None:
        return []
    result = value.split(",")
    require(all(result) and result == sorted(set(result)), f"{context}: tokens must be unique and sorted")
    return result


def derive_complexity(metrics: dict[str, int]) -> dict[str, object]:
    score = metrics["invocationCount"] * 8 + metrics["whenRuleReferenceCount"] * 6 + metrics["maxNesting"] * 5 + metrics["operationCount"] * 0.25 + metrics["loopCount"] * 10 + metrics["modifiedPropertyCount"] * 3 + metrics["pageParameterCount"] * 4 + metrics["conditionalBlockCount"] * 4 + metrics["unresolvedCriticalDependencyCount"] * 12
    thresholds = {"INVOCATION_COUNT": ("invocationCount", 10), "WHEN_RULE_REFERENCE_COUNT": ("whenRuleReferenceCount", 15), "MAX_NESTING": ("maxNesting", 6), "LOOP_COUNT": ("loopCount", 5), "MODIFIED_PROPERTY_COUNT": ("modifiedPropertyCount", 20), "UNRESOLVED_CRITICAL_DEPENDENCY_COUNT": ("unresolvedCriticalDependencyCount", 1), "PAGE_PARAMETER_COUNT": ("pageParameterCount", 5), "INVOCATION_CHAIN_DEPTH": ("invocationChainDepth", 6)}
    triggers = [code for code, (name, threshold) in thresholds.items() if metrics[name] >= threshold]
    if metrics["loopCount"] >= 1 and metrics["invocationCount"] >= 1:
        triggers.append("LOOP_INVOCATION_COMBINATION")
    high = bool(triggers) or score >= 50 or metrics["invocationChainDepth"] >= 2 or (metrics["whenRuleReferenceCount"] >= 3 and metrics["modifiedPropertyCount"] >= 8)
    tier = "HIGH" if high else "ELEVATED" if score >= 25 else "STANDARD"
    if tier == "STANDARD":
        confidence_cap, testability_cap = "High", "Testable"
    elif tier == "ELEVATED":
        confidence_cap, testability_cap = "Medium", "Testable"
    else:
        confidence_cap, testability_cap = ("Low" if metrics["unresolvedCriticalDependencyCount"] >= 1 else "Medium"), "PartiallyTestable"
    return {"score": score, "triggers": sorted(triggers), "tier": tier, "confidenceCap": confidence_cap, "testabilityCap": testability_cap}


def trace_escape(value) -> str:
    if value is None:
        return "-"
    return str(value).replace("&", "&amp;").replace("|", "&#124;").replace("\r", "&#13;").replace("\n", "&#10;").replace('"', "&quot;")


def trace_schema(record: dict) -> str:
    if record["tag"] == "ASSERT":
        return "ASSERT_DEC" if record["values"]["kind"] in {"DecisionInput", "DecisionResult"} else "ASSERT_STD"
    return record["tag"]


def project_trace(record: dict) -> str:
    schema = trace_schema(record)
    require(schema in TRACE_FIELDS, f"line {record['line']}: record is not trace-projectable")
    return "|".join([record["tag"], *(f"{field}={trace_escape(record['values'][field])}" for field in TRACE_FIELDS[schema])])


def validate_trace_text(value: str, schema: str) -> None:
    parts = value.split("|")
    tag = "ASSERT" if schema.startswith("ASSERT_") else schema
    require(parts[0] == tag, "trace tag")
    pairs = [part.split("=", 1) for part in parts[1:]]
    require(all(len(pair) == 2 for pair in pairs), "trace pair")
    require(tuple(pair[0] for pair in pairs) == TRACE_FIELDS[schema], f"{tag}: trace field whitelist/order")


def validate_typed(value_type, value, context: str) -> None:
    require(value_type in {"string", "boolean", "number", "null", "empty", "json", "absent"}, f"{context}: valueType")
    if value_type == "absent":
        require(value is None, f"{context}: absent value")
    elif value_type == "empty":
        require(value == "<EMPTY>", f"{context}: empty value")
    elif value_type == "null":
        require(value == "null", f"{context}: null value")
    elif value_type == "boolean":
        require(value in {"true", "false"}, f"{context}: boolean value")
    elif value_type == "number":
        parsed = canonical_json(value, context)
        require(isinstance(parsed, (int, float)) and not isinstance(parsed, bool), f"{context}: number value")
    elif value_type == "json":
        canonical_json(value, context)
    else:
        require(value is not None, f"{context}: string value")


def typed_python(value_type, value):
    if value_type == "absent":
        return None
    if value_type == "empty":
        return ""
    if value_type in {"boolean", "number", "null", "json"}:
        return json.loads(value)
    return value


def project_rut_parameter_value(formal_type, value_type, value, pages):
    """Static projection oracle for the original formal-type decision table.

    None means unavailable, never an inferred type or an emitted null value.
    The caller validates ledger value encoding before using this oracle.
    """
    if formal_type == "String" and value_type in {"string", "empty"}:
        return json.dumps("" if value_type == "empty" else value, ensure_ascii=False)
    if formal_type in {"Integer", "Decimal"} and value_type == "number":
        try:
            number = Decimal(value)
        except (InvalidOperation, TypeError):
            return None
        if not number.is_finite():
            return None
        if formal_type == "Integer":
            return str(int(number)) if number == number.to_integral_value() else None
        return format(number, "f")
    if formal_type in {"Boolean", "TrueFalse"} and value_type == "boolean" and value in {"true", "false"}:
        return value
    if formal_type == "PAGE" and value_type == "string" and value and value in pages:
        return value
    return None


def validate_formal_parameters(records, pages, context):
    """Check original-RUT type provenance without treating input bindings as formals."""
    kind = records[0]["values"]["kind"]
    scoped = defaultdict(dict)
    for record in records:
        values = record["values"]
        if "scenario" in values and "id" in values:
            scoped[values["scenario"]][values["id"]] = record
    formal_inputs = {}
    names = set()
    source_definitions = {}
    name_sources = {}
    for record in records:
        values = record["values"]
        if record["tag"] != "INPUT":
            continue
        in_param_namespace = values["path"].startswith("Param.")
        require(values["role"] != "DECISION_INPUT" or kind == "WHEN", f"{context}: DECISION_INPUT requires WHEN")
        require(not in_param_namespace or values["role"] in {"PARAM", "DECISION_INPUT"}, f"{context}: INPUT formal namespace/role")
        is_formal = values["role"] == "PARAM" or in_param_namespace
        if not is_formal:
            continue
        scenario = values["scenario"]
        parameter = scoped[scenario].get(values["resolution"], {})
        require(parameter.get("tag") == "PARAM", f"{context}: formal INPUT resolution")
        param = parameter["values"]
        require(param["dependency"] == "RUT" and values["path"] == "Param." + param["name"], f"{context}: formal RUT name/binding")
        key = (scenario, param["id"])
        require(key not in formal_inputs and (scenario, param["name"]) not in names, f"{context}: duplicate formal RUT input")
        formal_inputs[key] = values
        names.add((scenario, param["name"]))
        evidence = scoped[scenario].get(param["formalEvidence"], {})
        require(evidence.get("tag") == "EVIDENCE", f"{context}: missing formal type evidence")
        proof = evidence["values"]
        missing_declaration = proof["source"] == "RuleJSON/pyParameters"
        require(proof["kind"] == "RUT" and (missing_declaration or re.fullmatch(r"RuleJSON/pyParameters/(0|[1-9][0-9]*)", proof["source"]) is not None), f"{context}: formal type source")
        require(not missing_declaration or param["formalType"] is None, f"{context}: missing declaration has inferred type")
        require(param["formalEvidence"] in ids(param["evidence"], context, False), f"{context}: formal evidence not linked")
        fact = canonical_json(proof["fact"], context)
        require(isinstance(fact, dict) and set(fact) == {"pyParametersParamName", "pyParametersParamType"}, f"{context}: formal metadata shape")
        require(fact["pyParametersParamName"] == param["name"] and fact["pyParametersParamType"] == param["formalType"], f"{context}: formal metadata drift")
        require(param["formalType"] is None or isinstance(param["formalType"], str), f"{context}: formal type value")
        definition = (param["name"], param["formalType"])
        if not missing_declaration:
            require(source_definitions.setdefault(proof["source"], definition) == definition, f"{context}: inconsistent original formal definition")
        require(name_sources.setdefault(param["name"], proof["source"]) == proof["source"], f"{context}: ambiguous original formal name")
        if project_rut_parameter_value(param["formalType"], param["valueType"], param["value"], pages) is None:
            gaps = [r["values"] for r in records if r["tag"] == "GAP" and r["values"]["scenario"] == scenario]
            require(any(gap["code"] == "RUT_PARAMETER_PROJECTION_UNAVAILABLE" and gap["scope"] == values["path"] and gap["effect"] == "PARTIAL" and param["formalEvidence"] in ids(gap["evidence"], context, False) for gap in gaps), f"{context}: unavailable formal projection lacks GAP")
            meta = next(r["values"] for r in records if r["tag"] == "SCENARIO" and r["values"]["id"] == scenario)
            require(meta["testability"] in {"PartiallyTestable", "NotTestable"}, f"{context}: unavailable formal projection marked Testable")
    for record in records:
        if record["tag"] == "PARAM":
            values = record["values"]
            if (values["scenario"], values["id"]) not in formal_inputs:
                require(values["formalType"] is None and values["formalEvidence"] is None, f"{context}: non-formal PARAM has RUT type metadata")
        if record["tag"] == "COLUMN":
            values = record["values"]
            require((values["source"] == "PARAM") == values["path"].startswith("Param."), f"{context}: COLUMN formal namespace")


SIM_KEY_FIELDS = {
    "itemClass",
    "params",
    "payload",
    "pyClassName",
    "pyMockingSupportedRuleTypes",
    "pyRuleNameToBeMocked",
    "pySimulationMethod",
    "pxReferredFromClass",
    "setupPages",
    "shape",
    "sig",
    "target",
}


def validate_setup_pages(value, context: str) -> None:
    require(isinstance(value, list), f"{context}: setupPages must be an array")
    for page in value:
        require(isinstance(page, dict) and set(page) == {"pyPageDetails", "pySetupPageName"}, f"{context}: setup page shape")
        require(isinstance(page["pySetupPageName"], str) and page["pySetupPageName"], f"{context}: setup page name")
        require(isinstance(page["pyPageDetails"], list), f"{context}: page details")
        for detail in page["pyPageDetails"]:
            require(isinstance(detail, dict) and set(detail) == {"path", "value", "valueType"}, f"{context}: page detail shape")
            require(detail["valueType"] in {"string", "boolean", "number", "null", "empty", "json"}, f"{context}: page detail type")


def validate_simulation_key(value: str, context: str) -> list[dict]:
    if value == "NO_SIMULATION":
        return []
    parsed = canonical_json(value, context)
    require(isinstance(parsed, dict) and set(parsed) == {"simulations"}, f"{context}: key root shape")
    entries = parsed["simulations"]
    require(isinstance(entries, list) and entries, f"{context}: empty simulations")
    for entry in entries:
        require(isinstance(entry, dict) and set(entry) == SIM_KEY_FIELDS, f"{context}: simulation entry fields")
        require(isinstance(entry["params"], dict), f"{context}: params object")
        require(entry["shape"] in {"page", "list"}, f"{context}: shape")
        require(all(isinstance(entry[field], str) and entry[field] for field in ("pyClassName", "pyMockingSupportedRuleTypes", "pyRuleNameToBeMocked", "pySimulationMethod", "sig", "target")), f"{context}: required simulation values")
        require(entry["itemClass"] is None or isinstance(entry["itemClass"], str), f"{context}: itemClass")
        require(entry["shape"] != "list" or bool(entry["itemClass"]), f"{context}: list itemClass")
        require(entry["pxReferredFromClass"] is None or isinstance(entry["pxReferredFromClass"], str), f"{context}: referred class")
        validate_setup_pages(entry["setupPages"], context)
    return entries


def path_root(value: str) -> str:
    stripped = value.lstrip(".")
    return re.split(r"[.(]", stripped, maxsplit=1)[0]


def validate_ledger(path: Path, revision="1.1") -> dict:
    raw = path.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), f"{path.name}: BOM is forbidden")
    require(raw.endswith(b"\n"), f"{path.name}: final LF missing")
    require(b"\r" not in raw, f"{path.name}: raw CR is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractError(f"{path.name}: invalid UTF-8") from error
    lines = text[:-1].split("\n")
    require(lines and all(lines), f"{path.name}: blank record")
    records = [parse_line(line, index + 1, revision) for index, line in enumerate(lines)]
    require(records[0]["tag"] == "SG" and records[-1]["tag"] == "END", f"{path.name}: SG/END framing")
    require(sum(record["tag"] == "SG" for record in records) == 1, f"{path.name}: SG cardinality")
    require(sum(record["tag"] == "END" for record in records) == 1, f"{path.name}: END cardinality")

    header, end = records[0], records[-1]
    require(header["values"]["version"] == "1.1", f"{path.name}: version; rematerialize legacy v1 sources")
    require(end["values"]["complete"] == "PASS", f"{path.name}: incomplete payload")
    scenario_count = integer(header, "scenarioCount")
    group_order = integer(header, "groupOrder")
    require(group_order >= 1, f"{path.name}: groupOrder")
    require(header["values"]["groupId"] == f"G{group_order:03d}", f"{path.name}: deterministic groupId")

    body_start = 1
    require(records[body_start]["tag"] == "ROOT", f"{path.name}: ROOT position/cardinality")
    root = records[body_start]
    body_start += 1
    require(root["values"]["class"] == header["values"]["rutClass"], f"{path.name}: ROOT class")
    require(root["values"]["primarySetup"] in {"true", "false"}, f"{path.name}: ROOT primarySetup")
    pages = canonical_json(root["values"]["pagesAndClasses"], f"{path.name}:pagesAndClasses")
    require(isinstance(pages, dict) and pages.get(root["values"]["page"]) == root["values"]["class"], f"{path.name}: primary PagesAndClasses")
    named_evidence = canonical_json(root["values"]["namedPageEvidence"], f"{path.name}:namedPageEvidence")
    require(isinstance(named_evidence, list), f"{path.name}: named page evidence")
    for item in named_evidence:
        require(isinstance(item, dict) and set(item) == {"evidence", "page", "runtimeUse"} and item["runtimeUse"] in {"PAGE_PARAMETER", "EXECUTABLE_PATH", "PAGE_CREATION"}, f"{path.name}: named page evidence item")
    require(set(pages) - {root["values"]["page"]} == {item["page"] for item in named_evidence}, f"{path.name}: named page evidence coverage")

    target_rows = []
    while body_start < len(records) - 1 and records[body_start]["tag"] == "TARGET":
        target_rows.append(records[body_start])
        body_start += 1
    require(target_rows, f"{path.name}: no TARGET records")
    require([integer(row, "order") for row in target_rows] == list(range(1, len(target_rows) + 1)), f"{path.name}: TARGET order")
    target_ids = [row["values"]["id"] for row in target_rows]
    require(len(target_ids) == len(set(target_ids)) and all(ID_RE.fullmatch(value or "") for value in target_ids), f"{path.name}: TARGET IDs")
    require(all(row["values"]["state"] in {"REQUIRED", "BLOCKED", "UNREACHABLE", "EQUIVALENT"} for row in target_rows), f"{path.name}: TARGET state")
    required_targets = {row["values"]["id"] for row in target_rows if row["values"]["state"] == "REQUIRED"}
    require(all(row["values"]["proof"] is not None for row in target_rows if row["values"]["state"] != "REQUIRED"), f"{path.name}: TARGET proof")

    column_rows = []
    while body_start < len(records) - 1 and records[body_start]["tag"] == "COLUMN":
        column_rows.append(records[body_start])
        body_start += 1
    require([integer(row, "order") for row in column_rows] == list(range(1, len(column_rows) + 1)), f"{path.name}: COLUMN order")
    require(all(row["values"]["id"] == f"C{integer(row, 'order'):03d}" for row in column_rows), f"{path.name}: COLUMN IDs")
    require(all(row["values"]["source"] in {"PRIMARY", "PARAM", "PAGE"} and row["values"]["simulatedRoot"] == "false" for row in column_rows), f"{path.name}: COLUMN fields")

    control_tag = "CRAWL" if revision == "1.4" else "COMPLEXITY"
    require(records[body_start]["tag"] == control_tag, f"{path.name}: COMPLEXITY position/cardinality")
    complexity = records[body_start]
    body_start += 1
    metric_names = ("invocationCount", "whenRuleReferenceCount", "maxNesting", "operationCount", "loopCount", "modifiedPropertyCount", "conditionalBlockCount", "pageParameterCount", "unresolvedCriticalDependencyCount", "invocationChainDepth", "ruleCrawlerCalls", "dependencyReferencesRequested")
    if revision == "1.4": metric_names = ("ruleCrawlerCalls", "dependencyReferencesRequested")
    metrics = {name: integer(complexity, name) for name in metric_names}
    derived = derive_complexity(metrics) if revision != "1.4" else None
    if revision != "1.4": require(float(complexity["values"]["weightedScore"]) == derived["score"], f"{path.name}: weighted complexity score")
    if revision != "1.4": require(ids(complexity["values"]["hardTriggers"], f"{path.name}:hardTriggers") == derived["triggers"], f"{path.name}: hard triggers")
    if revision == "1.4": require(metrics["ruleCrawlerCalls"] <= 120 and metrics["dependencyReferencesRequested"] <= 260, "crawler budget exceeded")
    limits = []
    if metrics["ruleCrawlerCalls"] >= 120: limits.append("RULECRAWLER_CALL_CAP")
    if metrics["dependencyReferencesRequested"] >= 260: limits.append("RULES_TOTAL_REQUESTED_CAP")
    require(ids(complexity["values"]["triggeredLimits"], f"{path.name}:triggeredLimits") == sorted(limits), f"{path.name}: triggered limits")
    if revision != "1.4": require(complexity["values"]["tier"] == derived["tier"], f"{path.name}: complexity tier")
    if revision != "1.4": require(complexity["values"]["confidenceCap"] == derived["confidenceCap"] and complexity["values"]["testabilityCap"] == derived["testabilityCap"], f"{path.name}: complexity caps")

    scenario_rows = []
    while body_start < len(records) - 1 and records[body_start]["tag"] == "SCENARIO":
        scenario_rows.append(records[body_start])
        body_start += 1
    require(len(scenario_rows) == scenario_count, f"{path.name}: scenarioCount mismatch")
    scenario_ids = [row["values"]["id"] for row in scenario_rows]
    require(len(scenario_ids) == len(set(scenario_ids)), f"{path.name}: duplicate Scenario ID")
    require(all(ID_RE.fullmatch(value or "") for value in scenario_ids), f"{path.name}: invalid Scenario ID")
    require([integer(row, "order") for row in scenario_rows] == list(range(1, scenario_count + 1)), f"{path.name}: Scenario order")
    require(all(ids(row["values"]["covers"], f"{path.name}:covers", False) for row in scenario_rows), f"{path.name}: empty covers")
    covered_targets = set()
    for row in scenario_rows:
        covered = set(ids(row["values"]["covers"], f"{path.name}:covers", False))
        require(covered <= required_targets, f"{path.name}: covers unresolved/non-required TARGET")
        covered_targets.update(covered)
    require(covered_targets == required_targets, f"{path.name}: REQUIRED TARGET coverage")
    require(all(row["values"]["testability"] in {"Testable", "PartiallyTestable", "NotTestable"} for row in scenario_rows), f"{path.name}: testability")
    require(all(row["values"]["confidence"] in {"High", "Medium", "Low"} for row in scenario_rows), f"{path.name}: confidence")

    kind = header["values"]["kind"]
    rut_type = header["values"]["rutType"]
    key = header["values"]["simulationGroupKey"]
    if kind == "STANDARD":
        require(rut_type != "Rule-Obj-When" and scenario_count == 1 and key is None and not column_rows, f"{path.name}: STANDARD cardinality/key/columns")
        key_entries = []
    elif kind == "WHEN":
        require(rut_type == "Rule-Obj-When" and scenario_count >= 1 and key is not None and column_rows, f"{path.name}: WHEN cardinality/key/columns")
        key_entries = validate_simulation_key(key, f"{path.name}:simulationGroupKey")
    else:
        raise ContractError(f"{path.name}: invalid group kind")

    by_scenario_order = {row["values"]["id"]: integer(row, "order") for row in scenario_rows}
    body = records[body_start:-1]
    require(all(record["tag"] != "SCENARIO" for record in body), f"{path.name}: late SCENARIO")
    for record in body:
        scenario = record["values"].get("scenario")
        require(scenario in by_scenario_order, f"{path.name}: unknown Scenario reference at line {record['line']}")
    sort_keys = [(by_scenario_order[record["values"]["scenario"]], BODY_ORDER[record["tag"]], integer(record, "order")) for record in body]
    require(sort_keys == sorted(sort_keys), f"{path.name}: body record order")

    grouped = defaultdict(list)
    for record in body:
        grouped[(record["values"]["scenario"], record["tag"])].append(record)
    for (scenario, tag), rows in grouped.items():
        require([integer(row, "order") for row in rows] == list(range(1, len(rows) + 1)), f"{path.name}: {scenario}/{tag} order")

    seen = set()
    prefixes = {"PARAM": "K", "INPUT": "I", "SETUP": "U", "RX": "R", "DEP": "D", "BRANCH": "B", "PRODUCER": "P", "PROPERTY": "Y", "DTM": "Q", "DTE": "Q", "DTA": "Q", "DTC": "Z", "DTRA": "Q", "SIM": "M", "ASSERT": "A", "OMIT": "O", "EVIDENCE": "E", "GAP": "X", "SUMMARY": "H", "NARRATIVE": "N"}
    for record in body:
        scenario = record["values"]["scenario"]
        record_id = record["values"].get("id")
        if record_id is not None:
            require(ID_RE.fullmatch(record_id) is not None, f"{path.name}: invalid ID at line {record['line']}")
            require(re.fullmatch(prefixes[record["tag"]] + r"[0-9]{3}", record_id) is not None, f"{path.name}: non-deterministic local ID {record_id}")
            require((scenario, record_id) not in seen, f"{path.name}: duplicate Scenario-local ID {scenario}/{record_id}")
            seen.add((scenario, record_id))
    for scenario in scenario_ids:
        for prefix in set(prefixes.values()):
            numbers = sorted(int(record["values"]["id"][1:]) for record in body if record["values"]["scenario"] == scenario and record["values"].get("id", "").startswith(prefix))
            require(not numbers or numbers == list(range(1, len(numbers) + 1)), f"{path.name}: {scenario}/{prefix} ID sequence")

    confidence_rank = {"Low": 0, "Medium": 1, "High": 2}
    scenario_meta = {row["values"]["id"]: row["values"] for row in scenario_rows}
    for scenario in scenario_ids:
        scoped = [record for record in body if record["values"]["scenario"] == scenario]
        summary = next(record for record in scoped if record["tag"] == "SUMMARY")
        summary_values = summary["values"]
        scoped_counts = Counter(record["tag"] for record in scoped)
        require(integer(summary, "assertionCount") == scoped_counts["ASSERT"] and integer(summary, "omissionCount") == scoped_counts["OMIT"] and integer(summary, "simulationCount") == scoped_counts["SIM"] and integer(summary, "gapCount") == scoped_counts["GAP"], f"{path.name}: {scenario} SUMMARY counts")
        deps = [record["values"]["state"] for record in scoped if record["tag"] == "DEP"]
        if all(state == "NOT_APPLICABLE" for state in deps) and scoped_counts["GAP"] == 0:
            expected_dependency = "NotApplicable"
        elif all(state in {"CLOSED", "NOT_APPLICABLE"} for state in deps) and scoped_counts["GAP"] == 0:
            expected_dependency = "AllResolved"
        else:
            expected_dependency = "SomeUnresolved"
        require(summary_values["dependencyState"] == expected_dependency, f"{path.name}: {scenario} SUMMARY dependency state")
        expected_closure = "Closed" if expected_dependency in {"AllResolved", "NotApplicable"} else "Blocked"
        require(summary_values["dependencyClosureStatus"] == expected_closure, f"{path.name}: {scenario} SUMMARY closure state")
        simulation_state = summary_values["simulationState"]
        if simulation_state in {"NotRequired", "NotApplicable"}:
            require(scoped_counts["SIM"] == 0, f"{path.name}: {scenario} unexpected SIM records")
        elif simulation_state == "RequiredAndAligned":
            require(scoped_counts["SIM"] >= 1, f"{path.name}: {scenario} missing aligned SIM")
        elif simulation_state == "RequiredButLimited":
            require(scoped_counts["GAP"] >= 1, f"{path.name}: {scenario} limited simulation lacks GAP")
        else:
            raise ContractError(f"{path.name}: {scenario} invalid SUMMARY simulation state")
        branches = [record["values"]["result"] for record in scoped if record["tag"] == "BRANCH"]
        expected_branch = "SomeUnknown" if "UNKNOWN" in branches else "NotApplicable" if all(value == "NOT_APPLICABLE" for value in branches) else "AllEvaluated"
        require(summary_values["branchState"] == expected_branch, f"{path.name}: {scenario} SUMMARY branch state")
        support_rank = {"Structural": 0, "PredictedFromRules": 1, "Verified": 2}
        assertion_support = [record["values"]["support"] for record in scoped if record["tag"] == "ASSERT"]
        if scenario_meta[scenario]["testability"] == "NotTestable":
            expected_support = "NotTestable"
            require(not assertion_support, f"{path.name}: {scenario} NotTestable has ASSERT")
        elif scoped_counts["OMIT"]:
            expected_support = "OmittedClaimsPresent"
        else:
            require(assertion_support, f"{path.name}: {scenario} testable Scenario lacks ASSERT")
            highest_support = max(assertion_support, key=support_rank.get)
            expected_support = "StructuralOnly" if highest_support == "Structural" else highest_support
        require(summary_values["supportLevel"] == expected_support, f"{path.name}: {scenario} SUMMARY support level")
        gap_ids = sorted(record["values"]["id"] for record in scoped if record["tag"] == "GAP")
        require(ids(summary_values["blockingGaps"], f"{path.name}: {scenario} blocking gaps") == gap_ids, f"{path.name}: {scenario} SUMMARY gap census")
        if revision != "1.4": require(confidence_rank[scenario_meta[scenario]["confidence"]] <= confidence_rank[complexity["values"]["confidenceCap"]], f"{path.name}: {scenario} confidence cap")
        testability_rank = {"NotTestable": 0, "PartiallyTestable": 1, "Testable": 2}
        if revision != "1.4": require(testability_rank[scenario_meta[scenario]["testability"]] <= testability_rank[complexity["values"]["testabilityCap"]], f"{path.name}: {scenario} testability cap")
        checklist = set(sorted_tokens(summary_values["internalChecklist"], f"{path.name}: {scenario} checklist"))
        allowed_checklist = {"CELLS", "COVERAGE", "DECISION_TABLE", "DEPENDENCY", "ROOT", "SEED", "SIMULATION"}
        required_checklist = {"COVERAGE", "ROOT"}
        if kind == "WHEN": required_checklist.add("CELLS")
        if expected_dependency != "NotApplicable": required_checklist.add("DEPENDENCY")
        if scoped_counts["SIM"]: required_checklist.add("SIMULATION")
        if any(record["tag"] in {"DTM", "DTE", "DTA", "DTC", "DTRA"} for record in scoped): required_checklist.add("DECISION_TABLE")
        if scoped_counts["SETUP"] or scoped_counts["SIM"]: required_checklist.add("SEED")
        require(required_checklist <= checklist <= allowed_checklist, f"{path.name}: {scenario} checklist coverage")
        require(integer(summary, "maxDependencyWaveReached") == metrics["ruleCrawlerCalls"], f"{path.name}: {scenario} dependency wave count")

    for scenario in scenario_ids:
        tags = Counter(record["tag"] for record in body if record["values"]["scenario"] == scenario)
        for required in ("RX", "DEP", "BRANCH", "EVIDENCE", "SUMMARY", "NARRATIVE"):
            require(tags[required] >= 1, f"{path.name}: {scenario} lacks {required}")
        require(tags["SUMMARY"] == 1 and tags["NARRATIVE"] == 1, f"{path.name}: {scenario} summary/narrative cardinality")
        require(tags["ASSERT"] + tags["OMIT"] >= 1, f"{path.name}: {scenario} lacks final assertion decision")

    record_ids = defaultdict(dict)
    for record in body:
        record_id = record["values"].get("id")
        if record_id is not None:
            record_ids[record["values"]["scenario"]][record_id] = record
    all_evidence_ids = {record["values"]["id"] for record in body if record["tag"] == "EVIDENCE"}
    require(all(item["evidence"] in all_evidence_ids for item in named_evidence), f"{path.name}: unresolved named-page evidence")
    valid_pages = set(pages) | {"rowLevelPage"}
    for record in body:
        values = record["values"]
        if record["tag"] in {"INPUT", "SETUP", "ASSERT", "DTA"} and values.get("page") is not None:
            require(values["page"] in valid_pages, f"{path.name}: undeclared page at line {record['line']}")
            if values.get("class") is not None:
                expected_class = root["values"]["class"] if values["page"] == "rowLevelPage" else pages[values["page"]]
                require(values["class"] == expected_class, f"{path.name}: page/class drift at line {record['line']}")
        if record["tag"] in {"RX", "PRODUCER"}:
            require(values["context"] in pages, f"{path.name}: undeclared runtime context at line {record['line']}")
    for record in body:
        scenario = record["values"]["scenario"]
        evidence = record["values"].get("evidence")
        if evidence is not None:
            for reference in ids(evidence, f"{path.name}:evidence"):
                require(record_ids[scenario].get(reference, {}).get("tag") == "EVIDENCE", f"{path.name}: unresolved evidence {scenario}/{reference}")
        if record["tag"] == "ASSERT" and record["values"]["producer"] is not None:
            require(record_ids[scenario].get(record["values"]["producer"], {}).get("tag") == "PRODUCER", f"{path.name}: unresolved producer")
        if record["tag"] in {"RX", "BRANCH"}:
            for reference in ids(record["values"]["inputs"], f"{path.name}:{record['tag']} inputs"):
                require(record_ids[scenario].get(reference, {}).get("tag") in {"PARAM", "INPUT", "SETUP"}, f"{path.name}: unresolved {record['tag']} input")
        if record["tag"] == "RX" and record["values"]["guard"] is not None:
            require(record_ids[scenario].get(record["values"]["guard"], {}).get("tag") == "BRANCH", f"{path.name}: unresolved RX guard")
        if record["tag"] == "INPUT" and record["values"]["resolution"] is not None:
            resolution = record_ids[scenario].get(record["values"]["resolution"], {})
            require(resolution.get("tag") == "PARAM", f"{path.name}: unresolved INPUT resolution")
            require(resolution["values"]["valueType"] == record["values"]["valueType"] and resolution["values"]["value"] == record["values"]["value"], f"{path.name}: INPUT/PARAM value drift")
        if record["tag"] == "PRODUCER":
            require(record_ids[scenario].get(record["values"]["execution"], {}).get("tag") == "RX", f"{path.name}: unresolved execution")
            if record["values"]["guard"] is not None:
                require(record_ids[scenario].get(record["values"]["guard"], {}).get("tag") == "BRANCH", f"{path.name}: unresolved PRODUCER guard")
        if record["tag"] == "PROPERTY":
            for reference in ids(record["values"]["producers"], f"{path.name}:PROPERTY producers"):
                require(record_ids[scenario].get(reference, {}).get("tag") == "PRODUCER", f"{path.name}: unresolved PROPERTY producer")
        if record["tag"] == "GAP" and record["values"]["dependency"] is not None:
            require(record_ids[scenario].get(record["values"]["dependency"], {}).get("tag") == "DEP", f"{path.name}: unresolved dependency")
        if record["tag"] == "DTE":
            require(record_ids[scenario].get(record["values"]["dtm"], {}).get("tag") == "DTM", f"{path.name}: unresolved DTM")
            for reference in ids(record["values"]["actions"], f"{path.name}:actions"):
                require(record_ids[scenario].get(reference, {}).get("tag") == "DTA", f"{path.name}: unresolved DTA")
            for reference in ids(record["values"]["consumers"], f"{path.name}:consumers"):
                require(record_ids[scenario].get(reference, {}).get("tag") == "DTC", f"{path.name}: unresolved DTC")
        if record["tag"] == "DTA":
            require(record_ids[scenario].get(record["values"]["dte"], {}).get("tag") == "DTE", f"{path.name}: unresolved DTE")
        if record["tag"] == "DTC":
            require(record_ids[scenario].get(record["values"]["dte"], {}).get("tag") == "DTE", f"{path.name}: unresolved DTC/DTE")
            require(record_ids[scenario].get(record["values"]["decision"], {}).get("tag") in {"ASSERT", "OMIT"}, f"{path.name}: unresolved DTC decision")
        if record["tag"] == "DTRA":
            require(record_ids[scenario].get(record["values"]["dte"], {}).get("tag") == "DTE", f"{path.name}: unresolved DTRA/DTE")
            for reference in ids(record["values"]["checkedActions"], f"{path.name}:checkedActions"):
                require(record_ids[scenario].get(reference, {}).get("tag") == "DTA", f"{path.name}: unresolved checked DTA")
            for reference in ids(record["values"]["omitted"], f"{path.name}:omitted"):
                require(record_ids[scenario].get(reference, {}).get("tag") == "OMIT", f"{path.name}: unresolved OMIT")
        if record["tag"] == "SIM":
            for reference in ids(record["values"]["parameterResolutions"], f"{path.name}:parameterResolutions", revision == "1.4"):
                require(record_ids[scenario].get(reference, {}).get("tag") == "PARAM", f"{path.name}: unresolved SIM PARAM")
        if record["tag"] == "SUMMARY":
            for field in ("reasoningEvidence", "dependencyEvidence", "seedCoverageEvidence"):
                for reference in ids(record["values"][field], f"{path.name}:{field}", field != "reasoningEvidence"):
                    require(record_ids[scenario].get(reference, {}).get("tag") == "EVIDENCE", f"{path.name}: unresolved SUMMARY evidence")
            for reference in ids(record["values"]["blockingGaps"], f"{path.name}:blockingGaps"):
                require(record_ids[scenario].get(reference, {}).get("tag") == "GAP", f"{path.name}: unresolved SUMMARY gap")

    for record in body:
        values = record["values"]
        if record["tag"] == "PARAM":
            require(values["mode"] in ({"explicit", "inherited", "empty", "not_applicable"} | ({"default"} if revision == "1.4" else set())), f"{path.name}: PARAM mode")
            require(values["inheritance"] in {"enabled", "disabled", "n_a"}, f"{path.name}: PARAM inheritance")
            validate_typed(values["valueType"], values["value"], f"{path.name}:PARAM")
            require((values["mode"] in {"explicit", "inherited"}) == (values["expression"] is not None), f"{path.name}: PARAM expression")
        if record["tag"] == "INPUT":
            require(values["role"] in {"PARAM", "PRIMARY", "PAGE", "DECISION_INPUT"}, f"{path.name}: INPUT role")
            validate_typed(values["valueType"], values["value"], f"{path.name}:INPUT")
            require((values["role"] in {"PARAM", "DECISION_INPUT"}) == (values["resolution"] is not None), f"{path.name}: INPUT resolution cardinality")
        if record["tag"] == "SETUP":
            require(values["role"] in {"SETUP", "DTA_BEFORE", "PAGE_AND_CLASS"}, f"{path.name}: SETUP role")
            validate_typed(values["valueType"], values["value"], f"{path.name}:SETUP")
        if record["tag"] == "DEP" and values["parameters"] is not None:
            canonical_json(values["parameters"], f"{path.name}:DEP parameters")
        if record["tag"] == "DEP":
            require(values["kind"] in {"RUF", "DP", "HELPER", "DT", "NOT_APPLICABLE"}, f"{path.name}: DEP kind")
            require(values["state"] in {"CLOSED", "KEYONLY", "MISSING", "LIMIT", "OMIT_NONCRITICAL", "NOT_APPLICABLE"}, f"{path.name}: active DEP state")
        if record["tag"] == "BRANCH":
            require(values["result"] in {"TRUE", "FALSE", "UNKNOWN", "NOT_APPLICABLE"}, f"{path.name}: BRANCH result")
        if record["tag"] in {"PRODUCER", "SIM"}:
            canonical_json(values["payload"], f"{path.name}:{record['tag']} payload")
        if record["tag"] == "PROPERTY":
            require(values["support"] in {"Verified", "PredictedFromRules", "Structural", "Omitted"}, f"{path.name}: PROPERTY support")
            require(values["deterministic"] in {"true", "false"}, f"{path.name}: PROPERTY deterministic")
            validate_typed(values["valueType"], values["value"], f"{path.name}:PROPERTY")
        if record["tag"] == "DTM":
            require(values["mode"] in {"FIRST_MATCH", "EVALUATE_ALL"} and values["scalarEnabled"] in {"true", "false"}, f"{path.name}: DTM")
        if record["tag"] == "DTE":
            require(values["status"] in {"EXECUTED", "NOT_EXECUTED"} and values["scalarState"] in {"VALUE", "NONE"}, f"{path.name}: DTE")
            validate_typed(values["scalarType"], values["scalarValue"], f"{path.name}:DTE")
            require((values["scalarState"] == "NONE") == (values["scalarType"] == "absent"), f"{path.name}: DTE scalar state/type")
        if record["tag"] == "DTA":
            require(values["operation"] in {"SET", "ADD", "REMOVE", "CLEAR"} and values["status"] in {"EXECUTED", "NOT_EXECUTED"}, f"{path.name}: DTA")
            validate_typed(values["beforeType"], values["before"], f"{path.name}:DTA before")
            validate_typed(values["afterType"], values["after"], f"{path.name}:DTA after")
        if record["tag"] == "DTRA":
            require(values["pass"] in {"true", "false"}, f"{path.name}: DTRA pass")
        if record["tag"] == "SIM":
            require(values["sig"] not in {None, "", "NO_SIMULATION"}, f"{path.name}: invalid sig")
            canonical_json(values["params"], f"{path.name}:SIM params")
            require(values["method"] == "DefineData", f"{path.name}: SIM method")
            require(values["shape"] in {"page", "list"}, f"{path.name}: SIM shape")
            require(values["itemClass"] is not None if values["shape"] == "list" else True, f"{path.name}: list itemClass")
            setup_pages = canonical_json(values["setupPages"], f"{path.name}:SIM setupPages")
            validate_setup_pages(setup_pages, f"{path.name}:SIM setupPages")
            param_object = canonical_json(values["params"], f"{path.name}:SIM params")
            referenced_params = [record_ids[values["scenario"]][reference]["values"] for reference in ids(values["parameterResolutions"], f"{path.name}:SIM parameterResolutions", revision == "1.4")]
            require(param_object == {param["name"]: typed_python(param["valueType"], param["value"]) for param in referenced_params}, f"{path.name}: SIM/PARAM drift")
        if record["tag"] == "OMIT":
            require(values["reason"] in OMIT_REASONS, f"{path.name}: invalid omission reason")
        if record["tag"] == "ASSERT":
            require(values["kind"] in {"Property", "Page", "List", "ResultCount", "DecisionInput", "DecisionResult"}, f"{path.name}: ASSERT kind")
            require(values["support"] in {"Verified", "PredictedFromRules", "Structural"}, f"{path.name}: ASSERT support")
            if values["kind"] not in {"DecisionInput"} and values["value"] is not None:
                require(values["support"] in {"Verified", "PredictedFromRules"}, f"{path.name}: unsupported exact assertion")
            if values["kind"] == "DecisionInput":
                require(values["page"] == "rowLevelPage" and values["comparator"] == "Input Value", f"{path.name}: DecisionInput shape")
            if values["kind"] == "DecisionResult":
                require(values["page"] == "rowLevelPage" and values["target"] == "Result" and values["value"] in {"true", "false"}, f"{path.name}: DecisionResult shape")
        if record["tag"] == "EVIDENCE":
            require(values["kind"] in {"RUT", "DEPENDENCY", "EXECUTION", "SEED", "COVERAGE", "GATE"}, f"{path.name}: EVIDENCE kind")
            require(values["support"] in {"Verified", "PredictedFromRules", "Structural"} and values["confidence"] in {"High", "Medium", "Low"}, f"{path.name}: EVIDENCE support")
        if record["tag"] == "GAP":
            require(values["effect"] in {"OMITTED", "DOWNGRADED", "PARTIAL"}, f"{path.name}: GAP effect")
        if record["tag"] == "SUMMARY":
            require(values["supportLevel"] in {"Verified", "PredictedFromRules", "StructuralOnly", "OmittedClaimsPresent", "NotTestable"}, f"{path.name}: SUMMARY support")
            require(values["dependencyState"] in {"AllResolved", "SomeUnresolved", "NotApplicable"}, f"{path.name}: SUMMARY dependency")
            require(values["branchState"] in {"AllEvaluated", "SomeUnknown", "NotApplicable"}, f"{path.name}: SUMMARY branch")
            require(values["simulationState"] in {"NotRequired", "RequiredAndAligned", "RequiredButLimited", "NotApplicable"}, f"{path.name}: SUMMARY simulation")
            if revision != "1.4": require(values["complexityTier"] == complexity["values"]["tier"], f"{path.name}: SUMMARY complexity")
            require(integer(record, "queuedDependencyCount") == 0 and integer(record, "unscannedFetchedRuleJsonCount") == 0, f"{path.name}: active dependency work in SUMMARY")
            require(values["dependencyClosureStatus"] in {"Closed", "Blocked"}, f"{path.name}: SUMMARY closure")
        if record["tag"] == "NARRATIVE":
            require(integer(record, "order") == 1, f"{path.name}: NARRATIVE order")

    for scenario in scenario_ids:
        dtms = {record["values"]["id"]: record for record in body if record["tag"] == "DTM" and record["values"]["scenario"] == scenario}
        dtes = [record for record in body if record["tag"] == "DTE" and record["values"]["scenario"] == scenario]
        dtas = [record for record in body if record["tag"] == "DTA" and record["values"]["scenario"] == scenario]
        dtcs = [record for record in body if record["tag"] == "DTC" and record["values"]["scenario"] == scenario]
        dtras = [record for record in body if record["tag"] == "DTRA" and record["values"]["scenario"] == scenario]
        for dte in dtes:
            actions = {record["values"]["id"] for record in dtas if record["values"]["dte"] == dte["values"]["id"]}
            consumers = {record["values"]["id"] for record in dtcs if record["values"]["dte"] == dte["values"]["id"]}
            require(set(ids(dte["values"]["actions"], f"{path.name}:DTE actions")) == actions, f"{path.name}: incomplete DTE actions")
            require(set(ids(dte["values"]["consumers"], f"{path.name}:DTE consumers")) == consumers, f"{path.name}: incomplete DTE consumers")
            audits = [record for record in dtras if record["values"]["dte"] == dte["values"]["id"]]
            require(len(audits) == 1 and audits[0]["values"]["pass"] == "true", f"{path.name}: one passing DTRA per DTE")
            audit = audits[0]
            require(set(ids(audit["values"]["checkedActions"], f"{path.name}:DTRA actions")) == actions, f"{path.name}: DTRA action census")
            require(audit["values"]["source"] == dtms[dte["values"]["dtm"]]["values"]["source"], f"{path.name}: DTRA source")
            consumer_records = [record_ids[scenario][reference] for reference in consumers]
            if dte["values"]["scalarState"] == "NONE":
                mode = dtms[dte["values"]["dtm"]]["values"]["mode"]
                expected = "inactive_evaluate_all_scalar" if mode == "EVALUATE_ALL" else "inactive_return_values_scalar"
                omit_decisions = []
                targets = []
                for consumer in consumer_records:
                    decision = record_ids[scenario][consumer["values"]["decision"]]
                    require(decision["tag"] == "OMIT" and decision["values"]["target"] == consumer["values"]["target"] and decision["values"]["reason"] == expected, f"{path.name}: DEC-016 consumer omission")
                    require(not any(record["tag"] == "ASSERT" and record["values"]["scenario"] == scenario and record["values"]["target"] == consumer["values"]["target"] for record in body), f"{path.name}: inactive scalar ASSERT remains")
                    require(not any(record["tag"] == "PROPERTY" and record["values"]["scenario"] == scenario and record["values"]["target"] == consumer["values"]["target"] for record in body), f"{path.name}: inactive scalar propagation remains")
                    omit_decisions.append(decision["values"]["id"])
                    targets.append(consumer["values"]["target"])
                require(sorted_tokens(audit["values"]["removedScalar"], f"{path.name}:removedScalar") == sorted(targets), f"{path.name}: DTRA scalar target census")
                require(ids(audit["values"]["omitted"], f"{path.name}:DTRA omitted") == sorted(omit_decisions), f"{path.name}: DTRA omission census")
            else:
                for consumer in consumer_records:
                    decision = record_ids[scenario][consumer["values"]["decision"]]
                    require(decision["tag"] == "ASSERT" and decision["values"]["target"] == consumer["values"]["target"] and decision["values"]["value"] == dte["values"]["scalarValue"], f"{path.name}: scalar ASSERT consumer")
        require(len(dtras) == len(dtes), f"{path.name}: orphan DTRA")
        require(all(any(dte["values"]["dtm"] == dtm_id for dte in dtes) for dtm_id in dtms), f"{path.name}: orphan DTM")
        for action in dtas:
            require(sum(action["values"]["id"] in ids(dte["values"]["actions"], f"{path.name}:action membership") for dte in dtes) == 1, f"{path.name}: DTA DTE membership")
            if action["values"]["status"] == "EXECUTED":
                before = typed_python(action["values"]["beforeType"], action["values"]["before"])
                if action["values"]["beforeType"] != "absent":
                    require(any(record["tag"] == "SETUP" and record["values"]["scenario"] == scenario and record["values"]["role"] == "DTA_BEFORE" and record["values"]["path"] == action["values"]["target"] and record["values"]["page"] == action["values"]["page"] and record["values"]["class"] == action["values"]["class"] and record["values"]["valueType"] == action["values"]["beforeType"] and typed_python(record["values"]["valueType"], record["values"]["value"]) == before for record in body), f"{path.name}: missing DTA.before setup")
                after = typed_python(action["values"]["afterType"], action["values"]["after"])
                require(any(record["tag"] == "PROPERTY" and record["values"]["scenario"] == scenario and record["values"]["target"] == action["values"]["target"] and typed_python(record["values"]["valueType"], record["values"]["value"]) == after for record in body), f"{path.name}: lost DTA final effect")
                matching_assert = any(record["tag"] == "ASSERT" and record["values"]["scenario"] == scenario and record["values"]["target"] == action["values"]["target"] and record["values"]["page"] == action["values"]["page"] and record["values"]["class"] == action["values"]["class"] and record["values"]["value"] == action["values"]["after"] for record in body)
                matching_omit = any(record["tag"] == "OMIT" and record["values"]["scenario"] == scenario and record["values"]["target"] == action["values"]["target"] for record in body)
                require(matching_assert or matching_omit, f"{path.name}: undecided/inconsistent DTA final effect")
        before_setups = [record for record in body if record["tag"] == "SETUP" and record["values"]["scenario"] == scenario and record["values"]["role"] == "DTA_BEFORE"]
        require(all(any(action["values"]["target"] == setup["values"]["path"] and action["values"]["page"] == setup["values"]["page"] and action["values"]["class"] == setup["values"]["class"] for action in dtas) for setup in before_setups), f"{path.name}: orphan DTA_BEFORE setup")

    if kind == "WHEN":
        expected_sims = key_entries
        for scenario in scenario_ids:
            actual_sims = []
            for record in body:
                if record["tag"] == "SIM" and record["values"]["scenario"] == scenario:
                    values = record["values"]
                    actual_sims.append({"itemClass": values["itemClass"], "params": json.loads(values["params"]), "payload": json.loads(values["payload"]), "pyClassName": values["class"], "pyMockingSupportedRuleTypes": values["mockingRuleType"], "pyRuleNameToBeMocked": values["rule"], "pySimulationMethod": values["method"], "pxReferredFromClass": values["referredFromClass"], "setupPages": json.loads(values["setupPages"]), "shape": values["shape"], "sig": values["sig"], "target": values["target"]})
            require(actual_sims == expected_sims, f"{path.name}: {scenario} complete simulation/key drift")

        columns = [(row["values"]["path"], row["values"]["class"], row["values"]["mode"]) for row in column_rows]
        simulated_roots = {path_root(record["values"]["target"]) for record in body if record["tag"] == "SIM"}
        require(not any(path_root(path_value) in simulated_roots for path_value, _, _ in columns), f"{path.name}: simulated DP root in COLUMN")
        for scenario in scenario_ids:
            order = by_scenario_order[scenario]
            all_inputs = [record for record in body if record["tag"] == "INPUT" and record["values"]["scenario"] == scenario]
            inputs = [record for record in all_inputs if record["values"]["role"] == "DECISION_INPUT"]
            require(len(all_inputs) == len(inputs), f"{path.name}: {scenario} non-cell physical INPUT in WHEN group")
            input_signature = [(record["values"]["path"], record["values"]["class"], record["values"]["mode"]) for record in inputs]
            require(input_signature == columns, f"{path.name}: {scenario} DecisionColumnSignature drift")
            decision_inputs = [record for record in body if record["tag"] == "ASSERT" and record["values"]["scenario"] == scenario and record["values"]["kind"] == "DecisionInput"]
            require(len(decision_inputs) == len(inputs), f"{path.name}: {scenario} cell/trace cardinality")
            for input_record, assertion in zip(inputs, decision_inputs):
                require(integer(assertion, "row") == order, f"{path.name}: {scenario} DecisionInput row")
                require((assertion["values"]["target"], assertion["values"]["class"], assertion["values"]["mode"], assertion["values"]["value"]) == (input_record["values"]["path"], input_record["values"]["class"], input_record["values"]["mode"], input_record["values"]["value"]), f"{path.name}: {scenario} cell/trace value drift")
            results = [record for record in body if record["tag"] == "ASSERT" and record["values"]["scenario"] == scenario and record["values"]["kind"] == "DecisionResult"]
            require(len(results) == 1 and integer(results[0], "row") == order, f"{path.name}: {scenario} DecisionResult row/cardinality")

    counts = Counter(record["tag"] for record in body)
    expected_counts = {
        "targetCount": len(target_rows),
        "columnCount": len(column_rows),
        "paramCount": counts["PARAM"],
        "scenarioCount": scenario_count,
        "inputCount": counts["INPUT"],
        "setupCount": counts["SETUP"],
        "rxCount": counts["RX"],
        "depCount": counts["DEP"],
        "branchCount": counts["BRANCH"],
        "producerCount": counts["PRODUCER"],
        "propertyCount": counts["PROPERTY"],
        "dtCount": sum(counts[tag] for tag in ("DTM", "DTE", "DTA", "DTC", "DTRA")),
        "simCount": counts["SIM"],
        "assertCount": counts["ASSERT"],
        "omitCount": counts["OMIT"],
        "evidenceCount": counts["EVIDENCE"],
        "gapCount": counts["GAP"],
        "summaryCount": counts["SUMMARY"],
        "narrativeCount": counts["NARRATIVE"],
    }
    for field, expected in expected_counts.items():
        require(integer(end, field) == expected, f"{path.name}: END {field} mismatch")

    validate_formal_parameters(records, pages, path.name)
    return {
        "path": path,
        "payload": raw,
        "caseId": header["values"]["caseId"],
        "rutType": rut_type,
        "groupId": header["values"]["groupId"],
        "groupOrder": group_order,
        "kind": kind,
        "simulationGroupKey": key,
        "columnSignature": [(row["values"]["path"], row["values"]["class"], row["values"]["mode"]) for row in column_rows],
        "scenarioCount": scenario_count,
    }


def validate_write_result(result: dict) -> str | None:
    require(isinstance(result, dict) and set(result) == {"Success", "UUID", "ErrorCode", "ErrorMessage"}, "WriteMemory result shape")
    require(isinstance(result["Success"], bool) and all(isinstance(result[field], str) for field in ("UUID", "ErrorCode", "ErrorMessage")), "WriteMemory result types")
    if result["Success"]:
        require(result["UUID"] != "" and result["ErrorCode"] == "" and result["ErrorMessage"] == "", "WriteMemory success invariant")
        return result["UUID"]
    require(result["UUID"] == "" and result["ErrorCode"] in {"INVALID_INPUT", "UNSUPPORTED_TYPE", "WRITE_FAILED"} and result["ErrorMessage"] != "", "WriteMemory failure invariant")
    return None


def validate_orchestration(ledgers: dict[str, dict]) -> None:
    data = json.loads((FIXTURES / "orchestration.json").read_text(encoding="utf-8"))
    require(data.get("version") == 1, "orchestration version")
    for case in data["successfulHandoffs"]:
        names = case["groupFiles"]
        groups = [ledgers[name] for name in names]
        require([group["groupOrder"] for group in groups] == list(range(1, len(groups) + 1)), f"{case['name']}: group order")
        require(len({group["caseId"] for group in groups}) == 1, f"{case['name']}: CaseID drift")
        require(len({group["rutType"] for group in groups}) == 1, f"{case['name']}: RUTType drift")
        if groups[0]["kind"] == "WHEN":
            require(len({group["simulationGroupKey"] for group in groups}) == len(groups), f"{case['name']}: unequal keys merged")
        writes = case["expectedWrites"]
        require(len(writes) == len(groups), f"{case['name']}: write count")
        for write, name, group in zip(writes, names, groups):
            require(write == {"CaseID": group["caseId"], "Type": "ScenarioGroup", "PayloadFile": name}, f"{case['name']}: write arguments/order")
        uuids = [validate_write_result(result) for result in case["writeResults"]]
        require(all(value is not None for value in uuids), f"{case['name']}: write result")
        expected_call = {
            "CaseID": groups[0]["caseId"],
            "RUTType": groups[0]["rutType"],
            "ScenarioGroupUUIDs": uuids,
            "callCount": 1,
        }
        require(case["expectedGeneratorCall"] == expected_call, f"{case['name']}: Generator call")

    failure = data["writeFailure"]
    require(failure["expectedWriteAttempts"] == 2, "write failure attempt count")
    require(failure["retryCount"] == 0, "write failure retry prohibition")
    first_uuid = validate_write_result(failure["writeResults"][0])
    failed_uuid = validate_write_result(failure["writeResults"][1])
    require(first_uuid and failed_uuid is None and failure["writeResults"][1]["ErrorCode"] == "WRITE_FAILED", "write failure result")
    require(failure["expectedGeneratorCall"] is None, "partial Generator handoff is forbidden")
    require(failure["expectedOuterResponse"] == {"AIAgentResponseStatus": "Failed", "AIAgentErrorResponseMessage": "Scenario group storage failed."}, "write failure outer response")

    variants = data["simulationKeyFieldVariants"]
    base = variants["base"]
    require(set(base) == SIM_KEY_FIELDS, "simulation key base fields")
    seen_fields = set()
    canonical_base = json.dumps({"simulations": [base]}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    validate_simulation_key(canonical_base, "simulation key base")
    for variant in variants["variants"]:
        require(set(variant) == {"field", "value"} and variant["field"] in SIM_KEY_FIELDS, "simulation key variant shape")
        changed = dict(base)
        changed[variant["field"]] = variant["value"]
        canonical_changed = json.dumps({"simulations": [changed]}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        validate_simulation_key(canonical_changed, f"simulation key variant {variant['field']}")
        require(canonical_changed != canonical_base, f"simulation key field not discriminating: {variant['field']}")
        seen_fields.add(variant["field"])
    require(seen_fields == SIM_KEY_FIELDS and variants["noSimulation"] == "NO_SIMULATION" and validate_simulation_key("NO_SIMULATION", "no simulation") == [], "simulation key field/no-simulation coverage")

    for invalid in data["invalidWriteResponses"]:
        try:
            validate_write_result(invalid["response"])
        except ContractError:
            continue
        raise ContractError(f"malformed WriteMemory response accepted: {invalid['name']}")

    for mutation in data["negativeLedgerMutations"]:
        source = ledgers[mutation["source"]]["payload"].decode("utf-8")
        if mutation["operation"] == "replace":
            require(source.count(mutation["old"]) == 1, f"mutation source ambiguity: {mutation['name']}")
            mutated = source.replace(mutation["old"], mutation["new"])
        else:
            lines = source.splitlines(keepends=True)
            matches = [index for index, line in enumerate(lines) if line.startswith(mutation["prefix"])]
            require(len(matches) == 1, f"mutation line ambiguity: {mutation['name']}")
            index = matches[0]
            if mutation["operation"] == "deleteLinePrefix":
                del lines[index]
            elif mutation["operation"] == "duplicateLinePrefix":
                lines.insert(index + 1, lines[index])
            else:
                raise ContractError(f"unknown mutation operation: {mutation['operation']}")
            mutated = "".join(lines)
        try:
            validate_ledger(MemoryFixture(f"negative-{mutation['name']}.sgl", mutated.encode("utf-8")))
        except ContractError:
            continue
        raise ContractError(f"negative ledger mutation accepted: {mutation['name']}")

    expected = {
        "Completed": {"AIAgentResponseStatus": "Completed", "AIAgentErrorResponseMessage": ""},
        "PartiallyCompleted": {"AIAgentResponseStatus": "Completed", "AIAgentErrorResponseMessage": ""},
        "Failed": {"AIAgentResponseStatus": "Failed", "AIAgentErrorResponseMessage": "Unit test generation failed."},
        "MALFORMED": {"AIAgentResponseStatus": "Failed", "AIAgentErrorResponseMessage": "Unit test generator returned an invalid response."},
    }
    seen = set()
    for mapping in data["generatorStatusMappings"]:
        response = mapping["generatorResponse"]
        key = response.get("status", "MALFORMED")
        require(key in expected and mapping["outerResponse"] == expected[key], f"status mapping {key}")
        seen.add(key)
        outer = mapping["outerResponse"]
        require(set(outer) == {"AIAgentResponseStatus", "AIAgentErrorResponseMessage"}, f"status shape {key}")
        require(len(outer["AIAgentErrorResponseMessage"].split()) <= 20, f"status message bound {key}")
    require(seen == set(expected), "incomplete status mappings")

    for case in data["complexityCases"]:
        derived = derive_complexity(case["metrics"])
        require(derived == case["expected"], f"complexity case {case['name']}")

    projection = data["traceProjection"]
    source_text = (FIXTURES / projection["sourceFile"]).read_text(encoding="utf-8")
    records = [parse_line(line, index + 1) for index, line in enumerate(source_text.splitlines())]
    source = next(record for record in records if record["tag"] == projection["tag"] and record["values"].get("id") == projection["id"])
    actual_trace = project_trace(source)
    require(actual_trace == projection["expected"], "positive SIM trace projection")
    validate_trace_text(actual_trace, projection["tag"])
    require(all(f"{field}=" not in actual_trace for field in projection["forbiddenFields"]), "ScenarioGroup-only field leaked into trace")
    try:
        validate_trace_text(actual_trace + "|payload=forbidden", projection["tag"])
    except ContractError:
        pass
    else:
        raise ContractError("contaminated trace projection accepted")


def validate_slice() -> None:
    lines = SLICE.read_text(encoding="utf-8").splitlines()
    require(not any("NaN" in line for line in lines), "slice contains NaN placeholder")
    rows = [line for line in lines if line.startswith("| IPM-AUTH-")]
    require(len(rows) == 106, "slice row count")
    parsed = []
    for line in rows:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        require(len(cells) == 9, f"slice column count: {line[:30]}")
        match = IPM_RE.fullmatch(cells[0])
        require(match is not None, f"slice ID {cells[0]}")
        parsed.append(cells)
    source_rows = {}
    for line in S0_PLAN.read_text(encoding="utf-8").splitlines():
        if line.startswith("| IPM-AUTH-"):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            require(len(cells) == 9, f"source matrix column count: {line[:30]}")
            source_rows[cells[0]] = {"source": cells[1], "owner": cells[4], "migration": cells[5], "evidence": cells[7]}
    require(len(source_rows) == 106, "source matrix row count")
    require([int(IPM_RE.fullmatch(row[0]).group(1)) for row in parsed] == list(range(1, 107)), "slice IDs/order")
    owners = Counter(row[2] for row in parsed)
    require(owners == Counter({"SCENARIO_AUTHOR": 48, "SHARED_CONTRACT": 39, "UNIT_TEST_GENERATOR": 18, "VALIDATOR": 1}), f"slice owners {owners}")
    actions = Counter(row[3] for row in parsed)
    require(actions["SPLIT"] == 39 and actions["REMOVE_FROM_AUTHOR"] == 19 and actions["AUTHOR_KEEP"] + actions["AUTHOR_REPLACE"] == 48, f"slice actions {actions}")
    for row in parsed:
        source = source_rows[row[0]]
        require(row[1] == source["source"] and row[2] == source["owner"], f"slice source/owner drift {row[0]}")
        suffix = "author-half-presence-and-downstream-ownership-exclusion" if row[3] == "SPLIT" else "forbidden-author-responsibility-and-downstream-trace" if row[3] == "REMOVE_FROM_AUTHOR" else "required-semantic-destination-and-source-range-audit"
        expected_check = f"{source['evidence']}; check=S2-R{row[0][-3:]}-{suffix}"
        require(row[7] == expected_check, f"slice evidence/check drift {row[0]}")
        expected_action = "SPLIT" if source["owner"] == "SHARED_CONTRACT" else "REMOVE_FROM_AUTHOR" if source["owner"] in {"UNIT_TEST_GENERATOR", "VALIDATOR"} else "AUTHOR_REPLACE" if source["migration"] == "REPLACE" else "AUTHOR_KEEP"
        require(row[3] == expected_action, f"slice action drift {row[0]}")
        require("DEC-011" in row[6], f"slice decision trace {row[0]}")
        require(row[4] and row[5] and row[6] and row[7], f"slice incomplete {row[0]}")
        require(row[8] in {"NOT_STARTED", "IMPLEMENTED_NOT_VERIFIED", "VERIFIED"}, f"slice invalid status {row[0]}")
        if row[0] in PROFILE_IDS:
            require(row[8] in {"IMPLEMENTED_NOT_VERIFIED", "VERIFIED"} and "DEC-027" in row[6].split(","), f"slice profile review/decision {row[0]}")
        elif row[0] in FORMAL_PROVENANCE_IDS:
            require(row[8] in {"IMPLEMENTED_NOT_VERIFIED", "VERIFIED"} and "DEC-026" in row[6].split(","), f"slice formal-provenance review/decision {row[0]}")
        elif row[0] in BATCH1_IDS:
            require(row[8] == "VERIFIED", f"slice batch-1 status {row[0]}")
        elif row[0] in BATCH2_IDS:
            require(row[8] == "VERIFIED", f"slice batch-2 status {row[0]}")
        elif row[0] in BATCH3_IDS:
            require(row[8] in {"IMPLEMENTED_NOT_VERIFIED", "VERIFIED"}, f"slice batch-3 status {row[0]}")
        else:
            raise ContractError(f"slice unknown batch {row[0]}")
        if row[3] == "SPLIT":
            require(row[4] != row[5] and "None" not in row[4] and "None" not in row[5], f"slice invalid split {row[0]}")
        if row[3] == "REMOVE_FROM_AUTHOR":
            require(row[4].startswith("None; prohibit") and "Preserve downstream traceability" in row[5], f"slice invalid removal {row[0]}")

    catalog_lines = [line for line in lines if line.startswith("| S2-R")]
    require(len(catalog_lines) == 106, "row-check catalog count")
    catalog = []
    for line in catalog_lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        require(len(cells) == 6, f"row-check catalog column count: {line[:30]}")
        require(REGRESSION_RE.fullmatch(cells[0]) is not None, f"row-check ID {cells[0]}")
        catalog.append(cells)
    require([int(REGRESSION_RE.fullmatch(row[0]).group(1)) for row in catalog] == list(range(1, 107)), "row-check catalog IDs/order")
    require(len({row[0] for row in catalog}) == 106, "duplicate row-check ID")
    mode_by_action = {"AUTHOR_KEEP": "REQUIRE_AUTHOR_SEMANTICS", "AUTHOR_REPLACE": "REQUIRE_AUTHOR_SEMANTICS", "SPLIT": "SPLIT_OWNERSHIP", "REMOVE_FROM_AUTHOR": "FORBID_AUTHOR_OWNERSHIP"}
    for implementation, check in zip(parsed, catalog):
        require(check[1] == implementation[0] and check[0] == f"S2-R{implementation[0][-3:]}", f"row-check mapping {implementation[0]}")
        require(check[2] == mode_by_action[implementation[3]], f"row-check mode {implementation[0]}")
        if implementation[3] == "REMOVE_FROM_AUTHOR":
            expected_required = f"require_downstream_trace({implementation[5]})"
        else:
            expected_required = f"require_author_semantics({implementation[4]})"
        expected_forbidden = f"forbid_author_ownership({implementation[5]})" if implementation[3] in {"SPLIT", "REMOVE_FROM_AUTHOR"} else f"forbid_downstream_takeover({implementation[5]})"
        evidence = implementation[7].split("; check=", 1)[0]
        expected_audit = f"source={implementation[1]}; evidence={evidence}; decisions={implementation[6]}; phase=post-prompt"
        require(check[3] == expected_required and check[4] == expected_forbidden and check[5] == expected_audit, f"row-check executable definition {implementation[0]}")
    complexity_row = next(row for row in parsed if row[0] == "IPM-AUTH-041")
    complexity_check = next(row for row in catalog if row[0] == "S2-R041")
    require("DEC-020" in complexity_row[6].split(",") and "decisions=" + complexity_row[6] in complexity_check[5], "DEC-020 complexity row/check traceability")


def section(text: str, start: str, end: str) -> str:
    require(start in text and end in text, f"prompt section boundary {start}")
    return text.split(start, 1)[1].split(end, 1)[0]


def validate_prompt_batch1() -> None:
    raw = PROMPT.read_bytes()
    require(not raw.startswith(b"\xef\xbb\xbf"), "Main prompt BOM")
    text = raw.decode("utf-8")
    for row_id in BATCH1_IDS:
        require(row_id in text, f"Main prompt missing batch-1 trace {row_id}")

    core = section(text, "## 1. Scenario Author core contract", "## 1A. ScenarioGroup storage and UnitTestGenerator handoff")
    for token in ("You are the Pega Scenario Author", "minimum number of valid physical ScenarioGroups", "one complete replacement snapshot", "NO_SIMULATION", "never creates a UnitTestRules entry", "Visible output lock"):
        require(token in core, f"Main prompt core token {token}")
    require("legacy candidate, RuleCode, schema, Validator, and repair text only as downstream preservation evidence" in core, "Main prompt downstream authority lock")
    require("Sections 13–14" in core and "later bounded materialization batch" not in core and "not release-ready" not in core, "Main prompt executable grammar authority")

    handoff = section(text, "## 1A. ScenarioGroup storage and UnitTestGenerator handoff", "## 1B. Closed external-interface allowlist")
    for token in ("WriteMemory(CaseID=<exact pyID>, Type=\"ScenarioGroup\"", "Call WriteMemory exactly once per group", "do not retry", "UnitTestGenerator(CaseID=<exact pyID>", "Completed` or `PartiallyCompleted", "Unit test generator returned an invalid response."):
        require(token in handoff, f"Main prompt handoff token {token}")
    require("complete ScenarioGroup v1 grammar in Section 13" in handoff and "Until that grammar is present" not in handoff, "Main prompt active materialization contract")
    require(all(field in handoff for field in ("`Success`", "`UUID`", "`ErrorCode`", "`ErrorMessage`")), "Main prompt WriteMemory envelope")

    allowlist = section(text, "## 1B. Closed external-interface allowlist", "## 2. Source-of-truth order")
    allowed = re.findall(r"^- `([^`]+)`", allowlist, flags=re.MULTILINE)
    require(allowed == ["GetCaseData", "KnowledgeTool", "RuleCrawler", "WriteMemory", "UnitTestGenerator"], f"Main prompt allowlist {allowed}")
    for forbidden in ("MemoryTemp", "CreateAIAgentResponseRecord", "GetAIAgentResponseRecord", "GetMemory", "JsonValidationTool", "UnitTestValidator"):
        require(f"`{forbidden}`" in allowlist, f"Main prompt forbidden interface {forbidden}")
    require("Treat every other interface as unavailable" in allowlist and "must not be used to acquire UTC schema/example" in allowlist, "Main prompt closed allowlist scope")

    source_order = section(text, "## 2. Source-of-truth order", "## 3. KnowledgeTool semantic composite-key contract")
    require("ScenarioGroup v1 contract" in source_order and "UnitTestGenerator owns schema/example-guided projection" in source_order, "Main prompt source ownership")

    execution = section(text, "## 4. Required execution order", "## 5. Internal Evidence Ledger contract")
    require([int(value) for value in re.findall(r"^(\d+)\. ", execution, flags=re.MULTILINE)] == list(range(1, 21)), "Main prompt execution order")
    for token in ("CRAWL_STATUS=CLOSED", "Scenario Compiler through INVENTORY, WITNESSES, and FROZEN", "Form physical ScenarioGroups", "Call `WriteMemory` once per group", "call UnitTestGenerator exactly once"):
        require(token in execution, f"Main prompt execution token {token}")
    require("does not set RuleCode.pyPurpose" in execution and "invoke Validator" in execution, "Main prompt downstream execution exclusion")
    require("Semantic-scope lock for Sections 5–12" in text and "Sections 13–14 are the executable materialization and handoff authority" in text, "Main prompt semantic-scope lock")


EXECUTION_WORKFLOW_CRITICAL_CLAUSES = (
    "Run the Section 11 Scenario Compiler through INVENTORY, WITNESSES, and FROZEN",
    "run Author-owned AUDIT BASE and AUDITED against those semantic records",
)

COMPILER_WORKFLOW_CRITICAL_CLAUSES = (
    "A PASS is the final semantic pre-WriteMemory gate",
)

WORKFLOW_CRITICAL_CLAUSES = EXECUTION_WORKFLOW_CRITICAL_CLAUSES + COMPILER_WORKFLOW_CRITICAL_CLAUSES

ROOT_CRITICAL_CLAUSES = (
    "Derive ROOT.page directly from evidenced RUT/harness primary-page semantics when an explicit primary page is required; otherwise use `RunRecordPrimaryPage`. Never read or infer ROOT from RuleCode.",
    "ROOT.class = immutable original RuleJSON.pyClassName and must equal the ScenarioGroup RUT class.",
    "Freeze ROOT.page, ROOT.class, whether primary setup is required, the complete Pages & Classes mapping, and evidence for every runtime-used named page. Named-page evidence is allowed only for a PAGE parameter, explicit executable named-page path, or explicit page-creation operation.",
    "Record: ROOT|page=<page>|class=<class>|primarySetup=<true|false>|pagesAndClasses=<typedMap>|namedPageEvidence=<evidenceList>",
    "Resolve every leading-dot RUT path and every Primary.* path from ROOT.",
    "Generate semantic primary SETUP, Pages & Classes, Scenario CTX root, APB Primary root, and assertion intent from ROOT; UnitTestGenerator only projects these frozen facts.",
    "RUT pyPagesAndClasses does not select ROOT and never overrides the evidenced primary-page selection.",
)

DEC_020_CRITICAL_CLAUSES = (
    "Hard triggers use these exact codes and thresholds: `INVOCATION_COUNT` at invocation count ≥ 10, `WHEN_RULE_REFERENCE_COUNT` at When rule references ≥ 15, `MAX_NESTING` at max nesting ≥ 6, `LOOP_COUNT` at loop count ≥ 5, `MODIFIED_PROPERTY_COUNT` at modified properties ≥ 20, `UNRESOLVED_CRITICAL_DEPENDENCY_COUNT` at unresolved critical dependencies ≥ 1, `PAGE_PARAMETER_COUNT` at page parameters ≥ 5, and `INVOCATION_CHAIN_DEPTH` at invocation-chain depth ≥ 6.",
    "Weighted score formula: `INVOCATION_COUNT*8 + WHEN_RULE_REFERENCE_COUNT*6 + MAX_NESTING*5 + OPERATION_COUNT*0.25 + LOOP_COUNT*10 + MODIFIED_PROPERTY_COUNT*3 + PAGE_PARAMETER_COUNT*4 + CONDITIONAL_BLOCK_COUNT*4 + UNRESOLVED_CRITICAL_DEPENDENCY_COUNT*12`.",
    "The independent loop/invocation HIGH condition is exact: `loopCount >= 1 AND invocationCount >= 1`; add hard-trigger code `LOOP_INVOCATION_COMBINATION` when it applies.",
    "Set tier to HIGH when score ≥ 50, any hard-trigger code exists, invocation-chain depth ≥ 2, or When reference count ≥ 3 with modified property count ≥ 8. Otherwise set ELEVATED when 25 <= score < 50 and STANDARD when score < 25.",
    "Derive caps without discretion: STANDARD → `confidenceCap=High`, `testabilityCap=Testable`; ELEVATED → `confidenceCap=Medium`, `testabilityCap=Testable`; HIGH → `confidenceCap=Medium`, `testabilityCap=PartiallyTestable`. If unresolved critical dependency count ≥ 1, lower the HIGH confidence cap to `Low`; never raise either cap later.",
    "Set `triggeredLimits` to `RULECRAWLER_CALL_CAP` at 120 RuleCrawler calls and `RULES_TOTAL_REQUESTED_CAP` at 260 requested dependency references. Complexity increases internal trace depth. It must not reduce assertion coverage by itself.",
)

SEMANTIC_CRITICAL_CLAUSES = WORKFLOW_CRITICAL_CLAUSES + ROOT_CRITICAL_CLAUSES + DEC_020_CRITICAL_CLAUSES


def validate_semantic_critical(text: str) -> None:
    execution = section(text, "## 4. Required execution order", "## 5. Internal Evidence Ledger contract")
    root_lock = section(text, "### 5.3b RUT I/O Inventory and Seed-Direction Lock (mandatory)", "STEP 1 ")
    complexity = section(text, "### 5.6 LimitsAndComplexity ledger", "### 5.7 Scenario runtime execution rows")
    compiler = section(text, "### Scenario Compiler — sole authority for Scenario cardinality", "### 11D. Downstream projection reference — not executable by Scenario Author")
    for clause in SEMANTIC_CRITICAL_CLAUSES:
        require(text.count(clause) == 1, f"Main prompt critical semantic clause cardinality {clause}")
    for clause in EXECUTION_WORKFLOW_CRITICAL_CLAUSES:
        require(clause in execution, f"Main prompt execution-workflow clause {clause}")
    for clause in COMPILER_WORKFLOW_CRITICAL_CLAUSES:
        require(clause in compiler, f"Main prompt compiler-workflow clause {clause}")
    for clause in ROOT_CRITICAL_CLAUSES:
        require(clause in root_lock, f"Main prompt ROOT-lock clause {clause}")
    for clause in DEC_020_CRITICAL_CLAUSES:
        require(clause in complexity, f"Main prompt DEC-020 clause {clause}")
    for forbidden in ("After complete packaging, RuleCode", "then immediately CreateAIAgentResponseRecord", "tool serializer", "Each phase submits", "resubmit A", "ROOT.page = RuleCode"):
        require(forbidden not in compiler, f"Main prompt candidate-bound compiler text {forbidden}")
    require("Run I/W/F after dependency closure and before final ASSERT/SIM/OMIT decisions" in compiler, "Main prompt compiler I/W/F order")
    require("Run B/A only after those decisions, physical grouping, and complete ScenarioGroup materialization, but always before WriteMemory" in compiler, "Main prompt compiler B/A order")
    require("This is internal state, not a tool parameter" in compiler and "Each phase replaces the complete internal snapshot" in compiler, "Main prompt compiler carrier")
    require("AUDIT BASE (`B`). After final decisions, physical grouping, and complete ScenarioGroup materialization" in compiler, "Main prompt semantic B definition")
    require("AUDITED (`A`). From B only" in compiler and "materialized ScenarioGroup Scenario records" in compiler, "Main prompt semantic A definition")


def validate_prompt_batch2() -> None:
    text = PROMPT.read_text(encoding="utf-8")
    for row_id in BATCH2_IDS:
        require(row_id in text, f"Main prompt missing batch-2 trace {row_id}")

    knowledge = section(text, "## 3. KnowledgeTool semantic composite-key contract", "## 4. Required execution order")
    for token in ("requests only semantic KnowledgeArea content", "Never send a bare base area", "Maintain `KA`", "Deterministic acquisition checkpoints", "Missing required guidance remains an explicit gap"):
        require(token in knowledge, f"Main prompt semantic knowledge token {token}")
    require("UTC_KEYS" not in knowledge and "Rule-Test-Unit-Case key set" not in knowledge, "Main prompt retained UTC projection acquisition")

    evidence = section(text, "## 5. Internal Evidence Ledger contract", "## 6. Assertion discovery and resolution")
    require("Before freezing final Scenario decisions or materializing a ScenarioGroup" in evidence, "Main prompt evidence boundary")
    for row_id in ("IPM-AUTH-033", "IPM-AUTH-037", "IPM-AUTH-041", "IPM-AUTH-042"):
        require(row_id in evidence, f"Main prompt evidence trace {row_id}")

    dependency = section(text, "## 7. Dependency and RuleCrawler discipline", "## 8. RUF transitive discovery discipline")
    require("Closure and semantic handoff gates" in dependency and all(row in dependency for row in ("IPM-AUTH-048", "IPM-AUTH-056")), "Main prompt dependency semantic scope")

    simulation = section(text, "## 9. Property, context, branch, and simulation tracing", "## 10. Property semantics and assertion intent")
    require("Simulation decision materialization" in simulation and "Pre-handoff semantic simulation check" in simulation, "Main prompt simulation semantic scope")

    scenario = section(text, "## 11. Scenario formation and semantic decision freeze", "## 12. Final semantic summary and decision ledger")
    require("SCENARIO_SNAPSHOT" in scenario and "MemoryTemp" not in scenario, "Main prompt Scenario Compiler carrier replacement")
    require("ScenarioGroup count = count(distinct SIMULATION_GROUP_KEY)" in scenario and "Do not create UnitTestRules" in scenario, "Main prompt semantic grouping boundary")

    decisions = section(text, "## 12. Final semantic summary and decision ledger", "### 12.2 Final pre-materialization semantic gates")
    for token in ("Structured summary facts", "Rule-Obj-When cell and result decisions", "Final ASSERT/SIM/OMIT decisions", "Confidence and testability caps", "UnitTestGenerator, not Scenario Author, formats AssertionDecisionTrace"):
        require(token in decisions, f"Main prompt semantic decision token {token}")
    require(all(reason in decisions for reason in OMIT_REASONS), "Main prompt omission catalog")
    require("CreateAIAgentResponseRecord" not in decisions and "call Validator" not in decisions, "Main prompt semantic summary contains executable downstream call")
    validate_semantic_critical(text)
    for clause in SEMANTIC_CRITICAL_CLAUSES:
        mutated = text.replace(clause, "MUTATED_SEMANTIC_CONTRACT", 1)
        require(mutated != text, f"semantic mutation source missing {clause}")
        try:
            validate_semantic_critical(mutated)
        except ContractError:
            continue
        raise ContractError(f"semantic prompt mutation accepted: {clause}")
    for clause in SEMANTIC_CRITICAL_CLAUSES:
        relocated = text.replace(clause, "", 1) + f"\n{clause}\n"
        try:
            validate_semantic_critical(relocated)
        except ContractError:
            continue
        raise ContractError(f"relocated semantic prompt clause accepted: {clause}")


def semantic_contract_lines(value: str) -> list[str]:
    return [line.rstrip() for line in value.splitlines() if line.strip() and not line.startswith("#")]


def validate_prompt_integrity(raw: bytes) -> str:
    """Accept uniform LF or CRLF without relaxing any reviewed content byte."""
    require(not raw.startswith(b"\xef\xbb\xbf"), "Main prompt UTF-8 BOM forbidden")
    canonical = raw.replace(b"\r\n", b"\n")
    require(b"\r" not in canonical, "Main prompt lone CR forbidden")
    require(raw.count(b"\r\n") in (0, raw.count(b"\n")), "Main prompt mixed line endings forbidden")
    try:
        text = canonical.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContractError("Main prompt invalid UTF-8") from error
    require(canonical.count(b"\n") == FINAL_PROMPT_LINE_COUNT, "Main prompt final logical line count")
    require(hashlib.sha256(canonical).hexdigest().upper() == FINAL_PROMPT_SHA256, "Main prompt full-regression canonical-LF SHA-256")
    return text


def validate_prompt_portability() -> None:
    canonical = validate_prompt_integrity(PROMPT.read_bytes()).encode("utf-8")
    crlf = canonical.replace(b"\n", b"\r\n")
    require(validate_prompt_integrity(crlf) == validate_prompt_integrity(canonical), "Main prompt LF/CRLF equivalence")
    require(hashlib.sha256(crlf).hexdigest().upper() == FINAL_CRLF_PROMPT_SHA256, "Main prompt reviewed CRLF equivalence")
    mutations = {
        "semantic_content": canonical.replace(b"Scenario Author", b"Scenario Editor", 1),
        "boundary_whitespace": b" " + canonical,
        "missing_final_newline": canonical[:-1],
        "extra_newline": canonical + b"\n",
        "utf8_bom": b"\xef\xbb\xbf" + canonical,
        "lone_cr": canonical.replace(b"\n", b"\r", 1),
        "invalid_utf8": b"\xff" + canonical[1:],
        "mixed_line_endings": canonical.replace(b"\n", b"\r\n", 1),
    }
    for name, mutated in mutations.items():
        require(mutated != canonical, f"prompt integrity mutation source missing: {name}")
        try:
            validate_prompt_integrity(mutated)
        except ContractError:
            continue
        raise ContractError(f"prompt integrity mutation accepted: {name}")


def restore_closure_source_prompt(text):
    # Original-clause clarification only: preserve exact independently reviewed 1.3.
    ban = r"Reserved top-level system-page seed/input ban \(original Main 20–24\):[^\n]+\n\n"
    formula = r"For consumer validation only,[^\n]+\n\n"
    require(len(re.findall(ban,text)) == len(re.findall(formula,text)) == 1, "closure source definition boundaries")
    original = re.sub(ban,"",text)
    original = re.sub(formula,"The metric names, hard-trigger thresholds, and weighted-score formula are exactly those in the canonical Author complexity contract. ",original)
    require(hashlib.sha256(original.encode()).hexdigest().upper() == "9A3B1D8A060C78955024618E16DB3B4C85A1FD19A4009D604299A2C17E059FDD", "unchanged reviewed 1.3 outside closure source clarification")
    return original


def restore_projection_prompt(text):
    text = restore_closure_source_prompt(text)
    start = "#### 13.1.2 Revision 1.3 projection provenance"
    end = "### 13.2 Encoding"
    require(text.count(start) == 1, "projection provenance delta boundary")
    original = text[:text.index(start)] + text[text.index(end, text.index(start)):]
    original = original.replace("`SG|version=1.3|", "`SG|version=1.2|")
    original = original.replace("revision 1.3 below is now the required producer/consumer revision", "revision 1.2 below is now the required producer/consumer revision")
    original = original.replace("Revision 1.2 introduced this common profile; revision 1.3 below governs current producers and consumers. Generator rejects older or unknown revisions", "Producers emit `SG.version=1.2`; Generator rejects older or unknown revisions")
    original = original.replace("historical revision-1.2 examples are under fixtures/s3/profiled/.", "current producer/consumer examples are under fixtures/s3/profiled/.")
    require(hashlib.sha256(original.encode()).hexdigest().upper() == PROJECTION_BASELINE_SHA256, "unchanged instructions outside DEC-029 additions")
    return original


def restore_profile_prompt(text):
    text = restore_projection_prompt(text)
    start = "#### 13.1.1 Revision 1.2 source profile"
    end = "### 13.2 Encoding"
    require(text.count(start) == 1, "PROFILE prompt delta boundary")
    original = text[:text.index(start)] + text[text.index(end, text.index(start)):]
    original = original.replace("`SG|version=1.2|", "`SG|version=1.1|")
    original = original.replace("(`F` PROFILE, `C` COLUMN,", "(`C` COLUMN,")
    original = original.replace("6. for each scenario, its `PROFILE`, `PARAM`,", "6. for each scenario, its `PARAM`,")
    original = original.replace("Revision 1.1 originally added formal provenance; revision 1.2 below is now the required producer/consumer revision and rejects every older or unknown revision before projection.", "Producers emit `SG.version=1.1`; consumers reject legacy `version=1` and unknown revisions before projection.")
    require(hashlib.sha256(original.encode()).hexdigest().upper() == PROFILE_BASELINE_SHA256, "unchanged instructions outside DEC-027 additions")
    return original


def validate_formal_prompt_delta(text):
    """Remove only the declared DEC-026 additions and recover the reviewed S2 text."""
    original = restore_profile_prompt(text)
    for start, end in (
        ("Formal RUT metadata capture [", "### 5.3 BranchEvaluations ledger"),
        ("Revision 1.1 adds explicit formal RUT parameter provenance", "A ScenarioGroup payload is the complete, immutable semantic snapshot"),
        ("Formal RUT parameter provenance (IPM-AUTH-035/IPM-AUTH-078; DEC-026):", "#### 13.4.3 Execution and evidence"),
    ):
        require(original.count(start) == 1, f"formal prompt delta boundary: {start}")
        left = original.index(start)
        right = original.index(end, left)
        original = original[:left] + original[right:]
    formal_fields = "|formalType=<exactPegaTypeOrAbsent>|formalEvidence=<evidenceIDOrAbsent>"
    require(original.count(formal_fields) == 1 and original.count("SG|version=1.1|") == 1, "formal prompt grammar delta")
    original = original.replace(formal_fields, "").replace("SG|version=1.1|", "SG|version=1|")
    require(hashlib.sha256(original.encode()).hexdigest().upper() == S2_BASELINE_PROMPT_SHA256, "unchanged S2 instructions outside DEC-026 additions")


def validate_prompt_batch3() -> None:
    text = validate_prompt_integrity(PROMPT.read_bytes())
    validate_formal_prompt_delta(text)
    for row_id in BATCH3_IDS:
        require(row_id in text, f"Main prompt missing batch-3 trace {row_id}")

    gates = section(text, "### 12.2 Final pre-materialization semantic gates", "## 13. Executable ScenarioGroup v1 materialization contract")
    for token in (
        "When cell and trace gate",
        "Dependency evidence gate",
        "Assertion, setup, and seed gate",
        "Primary root gate",
        "Decision Table integration gate",
        "Final audit gate",
        "No positive exact assertion may depend on unresolved executable behavior",
        "do not delete a physical seed while retaining an old derived value",
        "Do not recompute Decision Table outcomes downstream",
        "Require A=PASS",
    ):
        require(token in gates, f"Main prompt final semantic gate {token}")

    materialization = section(text, "## 13. Executable ScenarioGroup v1 materialization contract", "## 14. Storage, handoff, and downstream ownership boundary")
    require("complete executable payload contract" in materialization and "Mandatory self-parse and completeness gate" in materialization, "Main prompt materialization authority")
    embedded_contract = section(materialization, "### 13.1 Purpose and boundary", "---")
    repository_contract = SCENARIO_CONTRACT.read_text(encoding="utf-8")
    repository_contract = section(repository_contract, "## Purpose and Boundary", "## Static Fixture Set")
    require(semantic_contract_lines(embedded_contract) == semantic_contract_lines(repository_contract), "Main prompt ScenarioGroup contract semantic synchronization")

    boundary = text.split("## 14. Storage, handoff, and downstream ownership boundary", 1)[1]
    require([int(value) for value in re.findall(r"^(\d+)\. ", section(boundary, "### 14.1 Author-owned final sequence", "### 14.2 Downstream preservation map"), flags=re.MULTILINE)] == list(range(1, 8)), "Main prompt final sequence")
    for token in (
        "WriteMemory` sequentially exactly once per group",
        "stop without retry, partial Generator handoff, deletion, overwrite, or payload exposure",
        "call UnitTestGenerator exactly once",
        "projects exactly one UnitTestRules entry per supplied physical group without merging, splitting, reordering",
        "new immutable UnitTestCandidate UUID",
        "Projection repair may correct only this mapping",
        "A semantic mismatch is rejected and reported",
        "Scenario Author never constructs or parses UnitTestRules candidate JSON",
        "The only persistence and delegation path is Section 14.1",
        "Schema descriptions, JSON examples, and UnitTestRules formatting are downstream Generator inputs",
    ):
        require(token in boundary, f"Main prompt final boundary token {token}")

    for legacy in (
        "### 12.2 CreateAIAgentResponseRecord and Validator loop",
        "### 12.3 — CreateAIAgentResponseRecord Exception Handling",
        "## 13. Final best-effort serialization pass before storage",
        "Final Scenario memory gate:",
        "Immediately after that A call, call:",
    ):
        require(legacy not in text, f"Main prompt retained legacy tail {legacy}")


def main() -> int:
    try:
        validate_prompt_portability()
        ledger_files = ("standard-escaping.sgl", "standard-not-testable.sgl", "when-key-a.sgl", "when-key-b.sgl", "when-no-simulation.sgl")
        ledgers = {name: validate_ledger(FIXTURES / name) for name in ledger_files}
        standard = ledgers["standard-escaping.sgl"]
        decoded_text = (FIXTURES / "standard-escaping.sgl").read_text(encoding="utf-8")
        setup_line = next(parse_line(line, 1) for line in decoded_text.splitlines() if line.startswith("SETUP|"))
        require(setup_line["values"]["value"] == "Ada|Lovelace\nC:\\Temp\tX", "escaping round trip")
        validate_orchestration(ledgers)
        validate_slice()
        validate_prompt_batch1()
        validate_prompt_batch2()
        validate_prompt_batch3()
    except (ContractError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}")
        return 1
    print("PASS: S2 design-freeze static validation")
    print("ledgers=5 scenarios=6 standard_groups=2 when_groups=3")
    print("slice_rows=106 row_checks=106 owners=48/39/18/1")
    print("dec016=sig,params,inactive_evaluate_all_scalar,inactive_return_values_scalar")
    print("orchestration=exact_s1_envelopes,ordered_writes,opaque_uuids,single_generator_call,no_retry,status_mappings")
    print("adversarial=invalid_write_envelopes:6,key_field_variants:12,ledger_mutations:12,trace_contamination:1")
    print("alternatives=zero_param,not_testable,required_but_limited,not_applicable,dta_omit")
    print("complexity=closed_tiers,caps,boundaries trace_projection=exact_whitelists")
    print("prompt_batch1=role,authority,allowlist,execution,result_boundary")
    print("prompt_batch2=knowledge,evidence,dependency,runtime,assertion,simulation,omission,scenario_freeze")
    print(f"prompt_batch2_mutations={len(SEMANTIC_CRITICAL_CLAUSES)}")
    print(f"prompt_batch2_relocations={len(SEMANTIC_CRITICAL_CLAUSES)}")
    print("prompt_batch3=final_gates,exact_scenariogroup_contract,ordered_storage,single_handoff,downstream_boundary")
    print(f"prompt_full_regression=canonical_lf_sha256:{FINAL_PROMPT_SHA256},ipm_rows:106")
    print("prompt_portability=uniform_lf_or_crlf,reviewed_crlf_equivalence,negative_mutations:8")
    print("dec026=revision_1.1,formal_type_provenance,projection_gaps,unchanged_s2_baseline_recovered")
    return 0


if __name__ == "__main__":
    sys.exit(main())

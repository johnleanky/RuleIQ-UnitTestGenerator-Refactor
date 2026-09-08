#!/usr/bin/env python3
"""Static DEC-026 handoff/projection boundary tests; no Pega runtime claims."""

from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import validate_s2_design as s2


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "s3"


def read_records(name):
    path = FIXTURES / name
    raw = path.read_bytes()
    s2.validate_ledger(s2.MemoryFixture(path.name, raw))
    return [s2.parse_line(line, i + 1) for i, line in enumerate(raw.decode("utf-8")[:-1].split("\n"))]


def payload(records):
    return ("\n".join(record["tag"] + "|" + "|".join(key + "=" + s2.encode_value(value) for key, value in record["values"].items()) for record in records) + "\n").encode()


def values(records, tag, identity=None):
    return next(record["values"] for record in records if record["tag"] == tag and (identity is None or record["values"].get("id") == identity))


def validate(records):
    return s2.validate_ledger(s2.MemoryFixture("formal-provenance.sgl", payload(records)))


def validate_source_parameters(records, declarations, context):
    """Compare handoff evidence to the complete synthetic original source array."""
    s2.require(isinstance(declarations, list), f"{context}: original parameter array")
    for record in records:
        if record["tag"] != "PARAM" or record["values"]["formalEvidence"] is None:
            continue
        param = record["values"]
        matches = [(index, item) for index, item in enumerate(declarations)
                   if isinstance(item, dict) and item.get("pyParametersParamName") == param["name"]]
        source = "RuleJSON/pyParameters"
        formal_type = None
        if len(matches) == 1:
            index, declaration = matches[0]
            source += f"/{index}"
            raw_type = declaration.get("pyParametersParamType")
            formal_type = raw_type if isinstance(raw_type, str) else None
        evidence = values(records, "EVIDENCE", param["formalEvidence"])
        expected = {"pyParametersParamName": param["name"], "pyParametersParamType": formal_type}
        s2.require(evidence["source"] == source, f"{context}: original declaration selection")
        s2.require(param["formalType"] == formal_type and json.loads(evidence["fact"]) == expected,
                   f"{context}: original declaration snapshot")


def reject_action(name, action, expected):
    try:
        action()
    except s2.ContractError as error:
        s2.require(expected in str(error), f"{name}: failed for unintended reason: {error}")
        return
    raise s2.ContractError(f"negative formal fixture accepted: {name}")


def reject(name, records, expected):
    reject_action(name, lambda: validate(records), expected)


def change_type(records, formal_type, missing_declaration=False):
    param = values(records, "PARAM", "K001")
    param["formalType"] = formal_type
    evidence = values(records, "EVIDENCE", "E002")
    evidence["fact"] = json.dumps({"pyParametersParamName": param["name"], "pyParametersParamType": formal_type}, sort_keys=True, separators=(",", ":"))
    if missing_declaration:
        evidence["source"] = "RuleJSON/pyParameters"


def add_projection_gap(records):
    input_path = values(records, "INPUT", "I001")["path"]
    gap = {"scenario": "S1", "id": "X001", "order": "1", "dependency": None, "code": "RUT_PARAMETER_PROJECTION_UNAVAILABLE", "scope": input_path, "effect": "PARTIAL", "evidence": "E002"}
    records.insert(next(i for i, record in enumerate(records) if record["tag"] == "SUMMARY"), {"tag": "GAP", "values": gap})
    summary = values(records, "SUMMARY")
    summary.update(gapCount="1", blockingGaps="X001", dependencyState="SomeUnresolved", dependencyClosureStatus="Blocked")
    summary["internalChecklist"] = ",".join(sorted(set(summary["internalChecklist"].split(",")) | {"DEPENDENCY"}))
    values(records, "SCENARIO")["testability"] = "PartiallyTestable"
    values(records, "END")["gapCount"] = "1"


def main():
    fixture = json.loads((FIXTURES / "rut-parameter-projection.json").read_text())
    for case in fixture["cases"]:
        s2.validate_typed(case["valueType"], case["value"], case["name"])
        actual = s2.project_rut_parameter_value(case["formalType"], case["valueType"], case["value"], {"RunRecordPrimaryPage": "App-Work-Customer"})
        s2.require(actual == case["expected"], f"formal type projection: {case['name']}")
        if case["formalType"] == "String" and actual is not None:
            expected_value = "" if case["valueType"] == "empty" else case["value"]
            s2.require(json.loads(actual) == expected_value, f"lossless string literal: {case['name']}")

    standard = read_records("rut-parameter-provenance.sgl")
    when = read_records("when-formal-parameter.sgl")
    raw_probes = 0
    with TemporaryDirectory(prefix="ruleiq-formal-bytes-") as directory:
        for name in ("rut-parameter-provenance.sgl", "when-formal-parameter.sgl"):
            raw = (FIXTURES / name).read_bytes()
            corruptions = (
                ("crlf", raw.replace(b"\n", b"\r\n"), "raw CR is forbidden"),
                ("missing_lf", raw[:-1], "final LF missing"),
                ("bom", b"\xef\xbb\xbf" + raw, "BOM is forbidden"),
                ("extra_lf", raw + b"\n", "blank record"),
            )
            for label, corrupted, message in corruptions:
                path = Path(directory) / name
                path.write_bytes(corrupted)
                reject_action(f"{name}:{label}", lambda: read_records(path), message)
                raw_probes += 1
    for name, records in (("standard", standard), ("when", when)):
        declarations = fixture["sourceParameters"][name]
        validate_source_parameters(records, declarations, name)

    source_probes = 0
    for name, records in (("standard", standard), ("when", when)):
        for duplicate_type in (values(records, "PARAM", "K001")["formalType"], "PAGE"):
            declarations = deepcopy(fixture["sourceParameters"][name])
            duplicate = deepcopy(declarations[0])
            duplicate["pyParametersParamType"] = duplicate_type
            declarations.append(duplicate)
            reject_action(f"{name}:duplicate", lambda: validate_source_parameters(records, declarations, name), "original declaration selection")
            source_probes += 1
    for case in fixture["sourceCases"]:
        records = deepcopy(when)
        change_type(records, case["expectedFormalType"])
        values(records, "EVIDENCE", "E002")["source"] = case["expectedSource"]
        if case["projectionGap"]:
            add_projection_gap(records)
        validate_source_parameters(records, case["declarations"], case["name"])
        validate(records)
        if case["projectionGap"]:
            reject_action(case["name"] + ":stale_handoff", lambda: validate_source_parameters(when, case["declarations"], case["name"]), "original declaration")
            source_probes += 1

    probes = []
    def probe(name, mutate, message, base=standard):
        records = deepcopy(base)
        mutate(records)
        probes.append((name, records, message))

    probe("missing_type_evidence", lambda r: values(r, "PARAM", "K001").update(formalEvidence=None), "missing formal type evidence")
    probe("changed_declared_type", lambda r: values(r, "PARAM", "K001").update(formalType="PAGE"), "formal metadata drift")
    probe("wrong_source_kind", lambda r: values(r, "EVIDENCE", "E002").update(kind="DEPENDENCY"), "formal type source")
    probe("wrong_source_path", lambda r: values(r, "EVIDENCE", "E002").update(source="RuleJSON/pySteps/0"), "formal type source")
    probe("unlinked_type_evidence", lambda r: values(r, "PARAM", "K001").update(evidence="E001"), "formal evidence not linked")
    probe("wrong_parameter_name", lambda r: values(r, "INPUT", "I001").update(path="Param.Other"), "formal RUT name/binding")
    probe("dependency_type_substitution", lambda r: values(r, "PARAM", "K001").update(dependency="D_Customer"), "formal RUT name/binding")
    probe("nonformal_metadata", lambda r: values(r, "PARAM", "K002").update(formalType="String"), "non-formal PARAM")
    probe("unknown_without_gap", lambda r: change_type(r, None), "unavailable formal projection lacks GAP")
    probe("invented_missing_declaration_type", lambda r: values(r, "EVIDENCE", "E002").update(source="RuleJSON/pyParameters"), "missing declaration has inferred type")
    probe("ambiguous_source_index", lambda r: values(r, "EVIDENCE", "E003").update(source="RuleJSON/pyParameters/0"), "inconsistent original formal definition")
    probe("when_namespace_disguise", lambda r: values(r, "COLUMN").update(source="PRIMARY"), "COLUMN formal namespace", when)
    def disguise_parameter(records, role):
        values(records, "INPUT", "I001").update(role=role, resolution=None)
        values(records, "PARAM", "K001").update(formalType=None, formalEvidence=None)
    for role in ("PRIMARY", "PAGE"):
        probe("param_namespace_as_" + role, lambda r, role=role: disguise_parameter(r, role), "INPUT formal namespace/role")
    probe("standard_decision_input", lambda r: values(r, "INPUT", "I001").update(role="DECISION_INPUT"), "DECISION_INPUT requires WHEN")
    probe("legacy_version", lambda r: values(r, "SG").update(version="1"), "version")
    probe("unknown_version", lambda r: values(r, "SG").update(version="2"), "version")
    def duplicate_input(records):
        duplicate = deepcopy(next(record for record in records if record["tag"] == "INPUT"))
        duplicate["values"].update(id="I007", order="7")
        records.insert(next(i for i, record in enumerate(records) if record["tag"] == "SETUP"), duplicate)
        values(records, "END")["inputCount"] = "7"
    probe("duplicate_formal_input", duplicate_input, "duplicate formal RUT input")
    def unknown_page(records):
        values(records, "PARAM", "K007")["value"] = "MissingPage"
        values(records, "INPUT", "I006")["value"] = "MissingPage"
    probe("unevidenced_page", unknown_page, "unavailable formal projection lacks GAP")
    def legacy_arity(records):
        values(records, "SG")["version"] = "1"
        for record in records:
            if record["tag"] == "PARAM":
                del record["values"]["formalType"]
                del record["values"]["formalEvidence"]
    probe("actual_legacy_arity", legacy_arity, "field order/arity mismatch")

    gap_cases = 0
    for base in (standard, when):
        for declared_type, missing in ((None, False), (None, True), ("Unknown", False), ("Date", False), ("", False)):
            records = deepcopy(base)
            change_type(records, declared_type, missing)
            add_projection_gap(records)
            validate(records)
            gap_cases += 1
        records = deepcopy(base)
        change_type(records, None)
        add_projection_gap(records)
        probe("wrong_gap_scope", lambda r: values(r, "GAP").update(scope="Param.Other"), "unavailable formal projection lacks GAP", records)
        probe("gap_not_linked_to_type", lambda r: values(r, "GAP").update(evidence="E001"), "unavailable formal projection lacks GAP", records)
        probe("unknown_marked_testable", lambda r: values(r, "SCENARIO").update(testability="Testable"), "unavailable formal projection marked Testable", records)
    for name, records, message in probes:
        reject(name, records, message)
    print(f"PASS: S3 parameter provenance; projection_cases={len(fixture['cases'])} ledgers=2 unavailable_type_cases={gap_cases} rejected_ledger_mutations={len(probes)} raw_source_cases={len(fixture['sourceCases'])} rejected_source_mutations={source_probes} rejected_raw_payloads={raw_probes}")
    print("scope=repository_static_only,no_generator_prompt,no_pega_runtime_claims")


if __name__ == "__main__":
    try:
        main()
    except (s2.ContractError, KeyError, TypeError, ValueError) as error:
        raise SystemExit(f"FAIL: {error}")

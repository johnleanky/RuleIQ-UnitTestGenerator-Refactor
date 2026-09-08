# S4 Existing Export Boundary

Status: VERIFIED implementation after independent final whole-stage gpt-6-astra/xhigh PASS and root reconciliation.

Baseline is S3 commit `4393c680633d176129676f7b91179262cc25391f`. Canonical Validator SHA-256 is `6143de7be3b7e35e796478bb1a3af553bd74832f6cc79ed92b6eb0af879e4353`; existing JsonValidator_tool.txt SHA-256 is `0435676946b22b62daa4405c0240005622c83dd419f322796321bbe05b0cb4b6`.

The export is an existing Rule-AI-Agent named UnitTestValidator, class RuleIQ-Work-GenUT, ruleset RuleIQApp/version01-03-02 and Claude-Sonnet-4-6 configuration. S4 preserves all identity, version, model, historical runtime metadata and unrelated bytes. It is not a new Rule-AI-Tool or backing implementation.

Exactly these regions may change:

1. The one pyGenAIDef/pySystemPrompt body, synchronized to the complete canonical prompt including report catalog/schema/examples. Replace HTML paragraphs in that body only.
2. The first root pzKnowledgeTools row (legacy candidate reader) becomes a minimal row containing only observed pxObjClass=Rule-AI-Tool and pyPurpose=GetMemory. Remove that obsolete row's copied category, action, confirmation and backing/runtime metadata instead of assigning them to an external tool. Preserve the JsonValidationTool and KnowledgeTool rows byte-for-byte, including all unrelated settings.
3. The first root pxRuleReferences row changes only pyRuleName and pxRuleFamilyName from the legacy reader to GetMemory/GETMEMORY. Preserve its other bytes and the remaining references.

The existing pyResponseStylePrompt already requires one raw JSON object with no prose and can remain unchanged. No new input-property XML schema, tool backing category, action configuration, RuleSet choice or model change is authorized. Deterministic synchronization must reconstruct the entire expected export from the fixed baseline plus these exact substitutions, and verify that reverting those regions returns identical baseline bytes. Validate the three-name tool allowlist and matching reference census through parsed XML as well as raw bytes. Named references do not prove Pega resolution/import/runtime.

## Implemented Artifact Evidence

The product batch passes `python -B scripts/validate_s4_design.py`; whole-stage independent verification passed and root reconciled the exact current manifest hashes. [build_s4_artifacts.py](../../../scripts/build_s4_artifacts.py) reproduces both artifacts from the verified contract, unchanged report schema/catalog and fixed export baseline. Exact XML paragraph decoding and restoration of all three allowed regions return the complete baseline bytes; four mutations reject prompt omission, model drift, tool broadening and appendix drift. The response-style prompt remains unchanged. Current hashes are recorded in the [artifact manifest](../../../fixtures/s4/artifact-manifest.json) and [acceptance report](S4-acceptance-report.md).

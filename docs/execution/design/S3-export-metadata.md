# S3 Agent Export Metadata Evidence

- **Status:** VERIFIED — complete prompt/export, observed metadata and parity received independent whole-stage PASS and root reconciliation. S3 CLOSED.
- **Sources:** read-only persisted fields in JsonValidator_tool.txt; reference-only Main_Agent.txt supplies the historical pyRuleVersionsList row1 pyLabel=01-05-02 (Available) and populated pzAgentTools serialization evidence. Main_Agent.txt is not an edit or parity target.

| Selected field | Value | Evidence/interpretation |
|---|---|---|
| pxObjClass | Rule-AI-Agent | Existing agent export root. |
| pyPurpose / pyRuleName | UnitTestGenerator | User-selected new rule name, DEC-014. |
| pyClassName | RuleIQ-Work-GenUT | Existing agent class. |
| pyRuleSet | RuleIQApp | Existing agent ruleset; unrelated to target test-rule selection. |
| pyRuleSetVersion | 01-05-02 | Deliberately selected from Main pyRuleVersionsList row1 pyLabel=01-05-02 (Available); its current root pyRuleSetVersion is 01-01-01 and root ruleset is a branch. This historical list entry is not a live availability/import claim. |
| pyAgentVersion | 1.0.0 | Existing agent contract version convention. |
| pyUsage | RuleIQ UT Generation | Exact existing Validator field. |
| pyRuleAvailable | Yes | Existing agent availability convention. |
| pyEnableExternalAccess | false | Existing private workflow setting. |
| pyGenAIConfig.pyModelConfiguration | Claude-Sonnet-4-6; bedrock/anthropic/Claude-Sonnet-4-6/v1; bedrock | Exact existing model fields; not the independent reviewer profile. |
| pyGenAIDef | Embed-GenAI-Definition, response-style prompt, system prompt, empty examples PageList | Existing persisted structure. |

The new export contains one pySystemPrompt element with one HTML paragraph per canonical prompt line. XML entity decoding and paragraph line joining recover the exact canonical text, including blank lines and symbols. This uses the observed HTML paragraph serialization; no invented Pega input/output property names are added. The complete named input/output contracts remain in the prompt as in existing exports.

The configured references contains exactly KnowledgeTool, GetMemory, WriteMemory and UnitTestValidator. The first three are named Rule-AI-Tool references in the observed pzKnowledgeTools list; the agent handoff is a named reference in pzAgentTools. Its observed serialized row class is also Rule-AI-Tool (Main pzAgentTools/rowdata with pyPurpose=UnitTestValidator and pyCategory=Agent); do not invent a Rule-AI-Agent row class. The new minimal reference retains pxObjClass/pyPurpose only and does not copy backing categories/actions. These references do not define, export or choose backing rules/categories for the external tools. Resolution to the user-implemented Pega rules remains external and unverified. Do not copy legacy tool backing activity names, response-record tools, RuleCrawler, or GetCaseData.

Do not copy creation/update operators, dates, system IDs, agent-card URLs, checkout locks, authorization/session state, toolbar state, or private rule caches. Root reference-only metadata is evidence, not a template for broad whole-file copying. Repository syntax, reference allowlist and decoded prompt parity are the acceptance boundary; live import and runtime remain unknown under DEC-019.

## Implemented artifact evidence

- UnitTestGenerator_Prompt.txt: SHA-256 `f62288bcf317f80f330052ab01d4c68d38ab39d7189256152dc055b7f2573c44`, 100904 bytes.
- UnitTestGenerator.txt: SHA-256 `283bded0bc62b95c99b5b1f1c0543d5dde1c445077c38024b2764b7b04f7449c`, 114726 bytes.

The builder copies only the documented runtime/validation requirements into the prompt and observed metadata/named references into XML. Full local parsing, paragraph/entity decoding, fixed manifest, source-contract/report mapping and reference/model checks pass. Live Pega import/resolution/runtime remain external.

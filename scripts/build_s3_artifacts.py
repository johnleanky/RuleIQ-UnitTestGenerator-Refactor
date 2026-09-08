#!/usr/bin/env python3
"""Deterministic repository artifact builder; never imports into or configures Pega."""
from pathlib import Path
import hashlib
import html
import json
import re

ROOT=Path(__file__).resolve().parents[1]


def canonical_prompt():
    contract=(ROOT/'docs/contracts/UNIT_TEST_GENERATOR_V1.md').read_text()
    runtime=contract[contract.index('## G1.'):contract.index('## G10.')]
    runtime=runtime.replace('[VALIDATOR_REPORT_S3.schema.json](VALIDATOR_REPORT_S3.schema.json)','the ValidatorReport schema in Appendix B')
    runtime=runtime.replace('[GENERATOR_RUN_REPORT_V1.schema.json](GENERATOR_RUN_REPORT_V1.schema.json)','the GeneratorRunReport schema in Appendix C')
    runtime=runtime.replace(' The static implementation may reuse the reviewed common grammar internally without changing the Memory payload or accepting legacy input.','')
    runtime=runtime.replace('Repository schema/example','Structural schema/example reference')
    source=(ROOT/'docs/contracts/SCENARIO_GROUP_V1.md').read_text()
    source=source[source.index('### Revision 1.2 source profile'):source.index('## Static Fixture Set')]
    source=source.replace(' The five S2 fixtures remain historical revision-1.1 regressions; historical revision-1.2 examples are under fixtures/s3/profiled/.','')
    source=source.replace('Revision-1.2 fixtures under fixtures/s3/profiled/ remain historical; current synthetic Author fixtures are under fixtures/s3/current/.','')
    g10='''## G10. Final Runtime Checks and Consumer Boundary

Before every write, complete the bidirectional frozen-source audit, current index map and selected-schema self-check from G2–G7. Before acting on Validator issues, validate the complete Appendix B report and G8 semantic route/coordinate constraints atomically. Return only the Appendix C report governed by G9. No success exists without the current candidate UUID receiving a valid OK report.

The configured Validator must implement this consumer contract. A legacy report with different fields, addresses, routes or semantic-rerun actions is malformed under G8. Never switch transport or weaken checks to accept it. Pega owns target Ruleset/Version selection and external tool implementation; this agent only copies the supplied metadata and invokes the four allowed interfaces.

## Appendix A. Complete Frozen Source Validation Reference

This reference describes the Scenario Author's immutable source contract. Producer actions, source acquisition, upstream phase restarts and ScenarioGroup writes belong exclusively to Scenario Author. Here, validate their recorded evidence and completeness; never perform those actions. Source violations follow G2. G1's four-interface allowlist and prohibition on source edits remain absolute. The current required wire revision is 1.3, whose additions override historical revision descriptions.

'''
    result='# UnitTestGenerator — System Prompt\n\n'+runtime+g10+source.rstrip()+'\n\n'
    for title,filename in [('Appendix B. ValidatorReport Structural Schema','VALIDATOR_REPORT_S3.schema.json'),('Appendix C. GeneratorRunReport Structural Schema','GENERATOR_RUN_REPORT_V1.schema.json')]:
        result+='## '+title+'\n\nThis schema is an in-prompt structural reference. Apply the additional semantic rules in G8/G9.\n\n```json\n'+(ROOT/'docs/contracts'/filename).read_text().strip()+'\n```\n\n'
    return result.rstrip()+'\n'


def export_text(prompt):
    def field(name,value):return '<'+name+'>'+html.escape(value,quote=False)+'</'+name+'>\n'
    output='<pagedata>\n'
    for name,value in [('pxObjClass','Rule-AI-Agent'),('pyRuleName','UnitTestGenerator'),('pyPurpose','UnitTestGenerator'),('pyLabel','Unit Test Generator'),('pyDescription','Projects immutable ScenarioGroups and validates versioned unit-test candidates.'),('pyClassName','RuleIQ-Work-GenUT'),('pyRuleSet','RuleIQApp'),('pyRuleSetVersion','01-05-02'),('pyAgentVersion','1.0.0'),('pyUsage','RuleIQ UT Generation'),('pyRuleAvailable','Yes'),('pyEnableExternalAccess','false')]:output+=field(name,value)
    output+='<pyGenAIConfig>\n<pxObjClass>Embed-GenAI-Config</pxObjClass>\n<pyModelConfiguration>\n<pxObjClass>Embed-GenAI-Model</pxObjClass>\n<pyModelName>Claude-Sonnet-4-6</pyModelName>\n<pyModelId>bedrock/anthropic/Claude-Sonnet-4-6/v1</pyModelId>\n<pyProvider>bedrock</pyProvider>\n</pyModelConfiguration>\n</pyGenAIConfig>\n'
    output+='<pyGenAIDef>\n<pxObjClass>Embed-GenAI-Definition</pxObjClass>\n<pyResponseStylePrompt><p>Return exactly one raw GeneratorRunReport JSON object and nothing else, including for failures. Do not emit UnitTestRules, Markdown, code fences, progress, analysis, or text outside that object.</p></pyResponseStylePrompt>\n<pySystemPrompt>'
    output+='\n'.join('<p>'+html.escape(line,quote=False)+'</p>' for line in prompt.splitlines())
    output+='</pySystemPrompt>\n<pyExamplesPageList REPEATINGTYPE="PageList"/>\n</pyGenAIDef>\n'
    for tag,names,kind in [('pzKnowledgeTools',['KnowledgeTool','GetMemory','WriteMemory'],'Rule-AI-Tool'),('pzAgentTools',['UnitTestValidator'],'Rule-AI-Tool')]:
        output+='<'+tag+' REPEATINGTYPE="PageList">\n'
        for i,name in enumerate(names,1):
            output+='<rowdata REPEATINGINDEX="'+str(i)+'">\n'+field('pxObjClass',kind)+field('pyPurpose',name)+'</rowdata>\n'
        output+='</'+tag+'>\n'
    return output+'<pzActionTools REPEATINGTYPE="PageList"/>\n</pagedata>\n'


def main():
    prompt=canonical_prompt();artifacts={'UnitTestGenerator_Prompt.txt':prompt,'UnitTestGenerator.txt':export_text(prompt)}
    for name,value in artifacts.items():(ROOT/name).write_text(value)
    manifest={name:hashlib.sha256(value.encode()).hexdigest() for name,value in artifacts.items()}
    (ROOT/'fixtures/s3/artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Built canonical Generator prompt, XML export and fixed integrity manifest.')


if __name__=='__main__':main()

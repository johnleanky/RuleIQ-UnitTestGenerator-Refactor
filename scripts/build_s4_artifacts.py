#!/usr/bin/env python3
"""Deterministic bounded synchronization of the existing Validator agent export."""
from pathlib import Path
import hashlib
import html
import json
import subprocess
import xml.etree.ElementTree as ET

from generator_protocol import CODE_ACTIONS
from validate_s2_design import require

ROOT=Path(__file__).resolve().parents[1]
BASE='4393c680633d176129676f7b91179262cc25391f'
PROMPT='Validator_Prompt.txt'
EXPORT='JsonValidator_tool.txt'


def baseline():return subprocess.check_output(['git','show',BASE+':'+EXPORT],cwd=ROOT).decode('utf-8')


def canonical_prompt():
    contract=(ROOT/'docs/contracts/UNIT_TEST_VALIDATOR_V1.md').read_text()
    body=contract[contract.index('## V1.'):contract.index('## V10.')].rstrip()
    body=body.replace('Use the complete closed schema reproduced in the runtime appendix; the repository authority remains VALIDATOR_REPORT_S3.schema.json.', 'Use the complete closed schema reproduced in Appendix B.')
    catalog='\n'.join('| '+code+' | '+', '.join(sorted(actions))+' |' for code,actions in CODE_ACTIONS.items())
    schema=(ROOT/'docs/contracts/VALIDATOR_REPORT_S3.schema.json').read_text().strip()
    examples=json.loads((ROOT/'fixtures/s4/report-examples.json').read_text())
    rendered='\n\n'.join('### '+name+'\n\n'+json.dumps(value,ensure_ascii=False,separators=(',',':')) for name,value in examples.items())
    return '# UnitTestValidator\n\n'+body+'\n\n## V10. Final output lock\n\nReturn exactly one raw ValidatorReport conforming to Appendix B, including input, tool and validation failures. Only the report is returned to UnitTestGenerator; no corrected candidate, other diagnostic object or surrounding prose. The closed catalog in Appendix A and complete examples in Appendix C are part of this contract.\n\n## Appendix A. Closed issue/action catalog\n\n| Issue code | Allowed action |\n|---|---|\n'+catalog+'\n\n## Appendix B. Complete ValidatorReport schema\n\n```json\n'+schema+'\n```\n\n## Appendix C. Runtime report examples\n\n'+rendered+'\n'


def prompt_span(text):
    require(text.count('<pySystemPrompt>')==text.count('</pySystemPrompt>')==1,'one prompt boundary')
    return text.index('<pySystemPrompt>')+len('<pySystemPrompt>'),text.index('</pySystemPrompt>')


def first_row_span(text,container):
    start=text.index('<'+container+' REPEATINGTYPE="PageList">')
    start=text.index('<rowdata REPEATINGINDEX="1">',start)
    end=text.index('<rowdata REPEATINGINDEX="2">',start)
    return start,end


def expected_export(prompt):
    text=baseline();a,b=prompt_span(text)
    text=text[:a]+'\n'+'\n'.join('<p>'+html.escape(line,quote=False)+'</p>' for line in prompt.splitlines())+'\n'+text[b:]
    a,b=first_row_span(text,'pzKnowledgeTools')
    require('<pyPurpose>GetAIAgentResponseRecord</pyPurpose>' in text[a:b],'legacy read row identified')
    text=text[:a]+'<rowdata REPEATINGINDEX="1">\n<pxObjClass>Rule-AI-Tool</pxObjClass>\n<pyPurpose>GetMemory</pyPurpose>\n</rowdata>\n'+text[b:]
    a,b=first_row_span(text,'pxRuleReferences');row=text[a:b]
    require(row.count('<pyRuleName>GetAIAgentResponseRecord</pyRuleName>')==1 and row.count('<pxRuleFamilyName>GETAIAGENTRESPONSERECORD</pxRuleFamilyName>')==1,'exact old reference names')
    row=row.replace('<pyRuleName>GetAIAgentResponseRecord</pyRuleName>','<pyRuleName>GetMemory</pyRuleName>').replace('<pxRuleFamilyName>GETAIAGENTRESPONSERECORD</pxRuleFamilyName>','<pxRuleFamilyName>GETMEMORY</pxRuleFamilyName>')
    return text[:a]+row+text[b:]


def verify_pair(prompt,export):
    require(prompt==canonical_prompt(),'complete verified runtime contract')
    require(export==expected_export(prompt),'bounded export bytes')
    tree=ET.fromstring(export);element=tree.find('pyGenAIDef/pySystemPrompt')
    require(element is not None,'prompt location')
    decoded='\n'.join(''.join(p.itertext()) for p in element.findall('p'))+'\n'
    require(decoded==prompt,'decoded Validator prompt/export parity')
    rows=tree.findall('./pzKnowledgeTools/rowdata')
    require([r.findtext('pyPurpose') for r in rows]==['GetMemory','JsonValidationTool','KnowledgeTool'],'closed tool order/census')
    require({c.tag for c in rows[0]}=={'pxObjClass','pyPurpose'} and rows[0].findtext('pxObjClass')=='Rule-AI-Tool','named-only external GetMemory')
    require([r.findtext('pyRuleName') for r in tree.findall('./pxRuleReferences/rowdata')]==['GetMemory','JsonValidationTool','KnowledgeTool'],'reference census')
    require(not tree.findall('./pzActionTools/rowdata') and not tree.findall('./pzAgentTools/rowdata'),'no write or agent reference')
    require(not any(word in export for word in ['GetAIAgentResponseRecord','CreateAIAgentResponseRecord','AUTHOR_REPAIR','AUTHOR_RERUN','RECONCILE_DECISION']),'removed legacy effective routes/transport')
    for n in range(1,11):require(prompt.count('## V'+str(n)+'.')==1,'complete runtime V section')
    for name in ['Appendix A.','Appendix B.','Appendix C.']:require(prompt.count('## '+name)==1,'runtime appendix')
    # Restore every allowed region and prove all remaining bytes are the baseline.
    old=baseline();restored=export
    for container in ['pzKnowledgeTools','pxRuleReferences']:
        a,b=first_row_span(restored,container);c,d=first_row_span(old,container)
        restored=restored[:a]+old[c:d]+restored[b:]
    a,b=prompt_span(restored);c,d=prompt_span(old);restored=restored[:a]+old[c:d]+restored[b:]
    require(restored==old,'exact baseline restoration outside approved regions')


def verify():
    prompt=(ROOT/PROMPT).read_text();export=(ROOT/EXPORT).read_text();verify_pair(prompt,export)
    manifest=json.loads((ROOT/'fixtures/s4/artifact-manifest.json').read_text())
    require(set(manifest)=={PROMPT,EXPORT},'artifact manifest census')
    for name,h in manifest.items():require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,'fixed S4 artifact hash '+name)
    for bad_prompt,bad_export in [(prompt.replace('GetMemory(CaseID, Type, UUID)','GetMemory(CaseID)',1),export),(prompt,export.replace('<pyModelName>Claude-Sonnet-4-6</pyModelName>','<pyModelName>Changed</pyModelName>',1)),(prompt,export.replace('<pyPurpose>GetMemory</pyPurpose>','<pyPurpose>WriteMemory</pyPurpose>',1)),(prompt,export.replace('Appendix B.','Appendix Z.',1))]:
        require((bad_prompt,bad_export)!=(prompt,export),'effective artifact mutation')
        try:verify_pair(bad_prompt,bad_export)
        except (ValueError,ET.ParseError):pass
        else:raise ValueError('artifact mutation accepted')


if __name__=='__main__':
    prompt=canonical_prompt();export=expected_export(prompt);verify_pair(prompt,export)
    (ROOT/PROMPT).write_text(prompt);(ROOT/EXPORT).write_text(export)
    manifest={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in [PROMPT,EXPORT]}
    (ROOT/'fixtures/s4/artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    verify();print('PASS: Validator prompt/export generated; exact parity and bounded baseline restoration')

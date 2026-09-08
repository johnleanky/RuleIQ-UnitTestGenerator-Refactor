#!/usr/bin/env python3
"""S3 design/stage gate: executable suites, source census, scope, links and artifact parity."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator
import validate_s2_design as b
import generator_protocol as protocol
import build_s3_artifacts as builder
import sg_profile

ROOT=Path(__file__).resolve().parents[1]
SUITES=['validate_s2_design.py','validate_s3_parameter_provenance.py','validate_s3_profiles.py','validate_s3_protocol.py','validate_s3_projection.py','validate_s3_flow.py','validate_s3_corrections.py']
CATEGORIES={'source','protocol','knowledge','metadata','parameters','setup','simulation','assertions','when','evidence','report','owner_preservation'}


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)


def matrix():
    source={}
    for line in (ROOT/'docs/execution/plans/S0-baseline-contracts.md').read_text().splitlines():
        if line.startswith(('| IPM-AUTH-','| IPM-VAL-')):
            c=[x.strip() for x in line.strip('|').split('|')];source[c[0]]=c
    catalog=json.loads((ROOT/'fixtures/s3/s3-row-regressions.json').read_text());slice_rows={}
    for line in (ROOT/'docs/execution/design/S3-instruction-implementation-slice.md').read_text().splitlines():
        if line.startswith(('| IPM-AUTH-','| IPM-VAL-')):
            c=[x.strip() for x in line.strip('|').split('|')];b.require(c[0] not in slice_rows,'duplicate S3 row');slice_rows[c[0]]=c
    b.require(len(source)==len(catalog)==len(slice_rows)==150 and set(source)==set(slice_rows),'complete 150-row S3 census')
    effective=0;generator=0;shared=0
    for ident,original in source.items():
        row=slice_rows[ident];case=catalog['S3-'+ident.replace('IPM-','')]
        b.require(len(row)==9 and row[1]==original[1] and row[2]==original[4] and row[5]==original[2],'exact original clause/owner: '+ident)
        b.require(case['row']==ident and case['source']==original[1] and case['obligation']==original[2] and case['disposition']==row[3] and case['case'] in CATEGORIES,'executable row binding: '+ident)
        if row[3] in {'IMPLEMENT','CONSUME_SHARED'}:
            effective+=1;b.require('UnitTestGenerator contract '+case['section'] in row[4] and row[8] in {'IMPLEMENTED_NOT_VERIFIED','VERIFIED'},'effective destination/status')
            if ident.startswith('IPM-AUTH-'):
                generator+=original[4]=='UNIT_TEST_GENERATOR';shared+=original[4]=='SHARED_CONTRACT'
        else:b.require(row[3] in {'EXCLUDED_AUTHOR','DEFERRED_S4','REMOVED_LEGACY'},'owner disposition')
        b.require('DEC-011' in row[6] and 'DEC-028' in row[6] and 'S3-'+ident.replace('IPM-','') in row[7],'decision/regression trace')
    b.require(generator==18 and shared==39,'all Generator/shared Author obligations')
    for commit_path in ['Main_Agent_Prompt.txt','Validator_Prompt.txt']:
        b.require(git('show','b9dd565:'+commit_path),'original source exists')
    return effective


def docs():
    paths=[ROOT/'docs/execution/CONTINUITY.md',ROOT/'docs/execution/ROADMAP.md',ROOT/'docs/execution/plans/S3-unit-test-generator.md',ROOT/'docs/contracts/UNIT_TEST_GENERATOR_V1.md',ROOT/'docs/execution/design/S3-instruction-implementation-slice.md']
    for path in paths:
        text=path.read_text()
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if re.match(r'[a-z]+:',link) or link.startswith('#'):continue
            target=link.split('#',1)[0]
            b.require(not target.startswith('/') and (path.parent/target).exists(),'local doc link: '+target)
    continuity=paths[0].read_text();plan=paths[2].read_text()
    matches=[]
    for text in [continuity,plan]:
        found=re.findall(r'^#{2,4} Exact [Nn]ext [Aa]ction\s*\n\s*([^\n]+)',text,re.M)
        b.require(len(found)==1,'one next action');matches.append(found[0])
    b.require(matches[0]==matches[1],'synchronized next action')
    return len(paths)


def scope(tracked=None):
    if tracked is None:tracked=git('ls-files','*.txt').decode().splitlines()
    active={'Main_Agent_Prompt.txt','UnitTestGenerator_Prompt.txt','UnitTestGenerator.txt','requirements-s3.txt'}
    others=[name for name in tracked if name not in active]
    b.require(len(others)==14,'legacy product census')
    for name in others:b.require((ROOT/name).read_bytes()==git('show','HEAD:'+name),'unchanged legacy product: '+name)
    caller='docs/contracts/PEGA_GENAI_TOOL_CALL_CONTRACTS.md'
    b.require((ROOT/caller).read_bytes()==git('show','HEAD:'+caller),'S1 contract unchanged')
    b.require(not list((ROOT/'scripts').glob('__pycache__')),'cache hygiene')


def future_tracking():
    """A future authorized commit must not count new artifacts as legacy files."""
    tracked=set(git('ls-files','*.txt').decode().splitlines())
    future=sorted(tracked | {'UnitTestGenerator_Prompt.txt','UnitTestGenerator.txt','requirements-s3.txt'})
    scope(future)
    try:scope(future+['UnexpectedLegacy.txt'])
    except b.ContractError:pass
    else:raise b.ContractError('unreviewed legacy product census accepted')


def reports():
    report=json.loads((ROOT/'docs/contracts/VALIDATOR_REPORT_S3.schema.json').read_text())
    run=json.loads((ROOT/'docs/contracts/GENERATOR_RUN_REPORT_V1.schema.json').read_text())
    for schema in [report,run]:Draft202012Validator.check_schema(schema)
    issue=report['properties']['issues']['items']
    b.require(set(issue['properties']['code']['enum'])==set(protocol.CODE_ACTIONS),'closed report codes')
    for rule in issue['allOf']:
        code=rule['if']['properties']['code']['const'];b.require(set(rule['then']['properties']['action']['enum'])==protocol.CODE_ACTIONS[code],'code/action schema sync')
    contract=(ROOT/'docs/contracts/UNIT_TEST_GENERATOR_V1.md').read_text()
    for code,actions in protocol.CODE_ACTIONS.items():b.require('| '+code+' | '+', '.join(sorted(actions))+' |' in contract,'prompt catalog sync')


def artifacts(design_only):
    prompt=ROOT/'UnitTestGenerator_Prompt.txt';export=ROOT/'UnitTestGenerator.txt'
    if design_only:
        b.require(not prompt.exists() and not export.exists(),'product implementation before design freeze');return
    b.require(prompt.exists() and export.exists(),'Generator prompt/export not implemented')
    # Final artifact implementation fills the independently frozen checks below.
    raw=export.read_text();b.require(raw.count('<pySystemPrompt>')==raw.count('</pySystemPrompt>')==1,'one prompt boundary')
    tree=ET.fromstring(raw);element=tree.find('pyGenAIDef/pySystemPrompt')
    b.require(element is not None,'embedded prompt location')
    decoded='\n'.join(''.join(p.itertext()) for p in element.findall('p'))+'\n'
    expected=prompt.read_text();b.require(decoded==expected,'decoded Generator prompt/export parity')
    b.require(expected==builder.canonical_prompt(),'complete frozen contract/source/report prompt mapping')
    for name,value in {'pxObjClass':'Rule-AI-Agent','pyPurpose':'UnitTestGenerator','pyRuleName':'UnitTestGenerator','pyClassName':'RuleIQ-Work-GenUT','pyRuleSet':'RuleIQApp','pyRuleSetVersion':'01-05-02','pyEnableExternalAccess':'false'}.items():b.require(tree.findtext(name)==value,'agent metadata '+name)
    references=[e.findtext('pyPurpose') for e in tree.findall('./pzKnowledgeTools/rowdata')+tree.findall('./pzAgentTools/rowdata')+tree.findall('./pzActionTools/rowdata')]
    b.require(len(references)==4 and set(references)=={'KnowledgeTool','GetMemory','WriteMemory','UnitTestValidator'},'closed export interface list')
    b.require(not any(tree.iter(name) and list(tree.iter(name)) for name in ['pyIntentActionPage','pyAgentCardURL','pxCreateOperator','pxUpdateOperator']),'no invented backing or copied runtime identity')
    for section in range(1,11):b.require('## G'+str(section)+'.' in expected,'complete prompt contract section')
    for section in ['## Appendix A.', '## Appendix B.', '## Appendix C.']:b.require(expected.count(section)==1,'self-contained runtime appendix')
    original=git('show','b9dd565:Main_Agent_Prompt.txt').decode('utf-8-sig')
    clause=original.split('Reserved top-level system-page seed ban:',1)[1].split('This applies',1)[0]
    banned=set(re.findall(r'`([^`]+)`',clause))
    b.require(banned==sg_profile.RESERVED_ROOTS and all('`'+name+'`' in expected for name in banned),'original closed reserved-root list in source gate/prompt')
    source_formula=re.search(r'Weighted score formula: `([^`]+)`',original).group(1)
    metrics={'INVOCATION_COUNT':'invocationCount','WHEN_RULE_REFERENCE_COUNT':'whenRuleReferenceCount','MAX_NESTING':'maxNesting','OPERATION_COUNT':'operationCount','LOOP_COUNT':'loopCount','MODIFIED_PROPERTY_COUNT':'modifiedPropertyCount','PAGE_PARAMETER_COUNT':'pageParameterCount','CONDITIONAL_BLOCK_COUNT':'conditionalBlockCount','UNRESOLVED_CRITICAL_DEPENDENCY_COUNT':'unresolvedCriticalDependencyCount'}
    formula=re.sub(r'[A-Z_]+',lambda m:metrics[m.group()],source_formula)
    b.require('weightedScore = '+formula in expected,'original complexity arithmetic is self-contained')
    for code,(metric,threshold) in {'INVOCATION_COUNT':('invocationCount',10),'WHEN_RULE_REFERENCE_COUNT':('whenRuleReferenceCount',15),'MAX_NESTING':('maxNesting',6),'LOOP_COUNT':('loopCount',5),'MODIFIED_PROPERTY_COUNT':('modifiedPropertyCount',20),'UNRESOLVED_CRITICAL_DEPENDENCY_COUNT':('unresolvedCriticalDependencyCount',1),'PAGE_PARAMETER_COUNT':('pageParameterCount',5),'INVOCATION_CHAIN_DEPTH':('invocationChainDepth',6)}.items():
        b.require(code+': '+metric+'>='+str(threshold) in expected,'self-contained trigger threshold '+code)
    for path,value in {'pyUsage':'RuleIQ UT Generation','pyAgentVersion':'1.0.0','pyRuleAvailable':'Yes','pyGenAIConfig/pxObjClass':'Embed-GenAI-Config','pyGenAIConfig/pyModelConfiguration/pxObjClass':'Embed-GenAI-Model','pyGenAIConfig/pyModelConfiguration/pyModelName':'Claude-Sonnet-4-6','pyGenAIConfig/pyModelConfiguration/pyModelId':'bedrock/anthropic/Claude-Sonnet-4-6/v1','pyGenAIConfig/pyModelConfiguration/pyProvider':'bedrock','pyGenAIDef/pxObjClass':'Embed-GenAI-Definition'}.items():b.require(tree.findtext(path)==value,'observed export metadata '+path)
    for tag,kind in [('pzKnowledgeTools','Rule-AI-Tool'),('pzAgentTools','Rule-AI-Tool')]:
        for row in tree.findall(tag+'/rowdata'):b.require({c.tag for c in row}=={'pxObjClass','pyPurpose'} and row.findtext('pxObjClass')==kind,'named-only external reference')
    style=''.join(tree.find('pyGenAIDef/pyResponseStylePrompt').itertext())
    b.require('GeneratorRunReport' in style and 'including for failures' in style,'runtime-only report style')
    manifest=json.loads((ROOT/'fixtures/s3/artifact-manifest.json').read_text())
    for path in [prompt,export]:b.require(hashlib.sha256(path.read_bytes()).hexdigest()==manifest[path.name],'fixed artifact integrity')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--design-only',action='store_true');args=parser.parse_args()
    effective=matrix();count=docs();scope();future_tracking();reports();artifacts(args.design_only)
    for name in SUITES:
        result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts'/name)],cwd=ROOT,text=True,capture_output=True)
        b.require(result.returncode==0,name+': '+result.stdout+result.stderr)
        print(result.stdout.splitlines()[0])
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,check=True)
    print(f'PASS: S3 {"design" if args.design_only else "artifact"} gate; rows=150 effective={effective} Generator=18 sharedAuthor=39 docs={count}; independent review evidence is recorded separately')


if __name__=='__main__':
    try:main()
    except (b.ContractError,KeyError,TypeError,ValueError) as error:raise SystemExit('FAIL: '+str(error))
